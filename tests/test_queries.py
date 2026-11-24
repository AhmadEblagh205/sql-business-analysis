import sqlite3
from pathlib import Path

import pandas as pd

from download_data import EXPECTED_TABLES, validate_database

ROOT = Path(__file__).resolve().parents[1]
SQL_DIR = ROOT / "sql"


def _fixture_db():
    con = sqlite3.connect(":memory:")
    con.executescript(
        """
        CREATE TABLE Employee (
            EmployeeId INTEGER PRIMARY KEY,
            LastName TEXT, FirstName TEXT, HireDate TEXT
        );
        CREATE TABLE Customer (
            CustomerId INTEGER PRIMARY KEY,
            Country TEXT,
            SupportRepId INTEGER
        );
        CREATE TABLE Invoice (
            InvoiceId INTEGER PRIMARY KEY,
            CustomerId INTEGER,
            InvoiceDate TEXT,
            BillingCountry TEXT,
            Total REAL
        );
        CREATE TABLE Genre (GenreId INTEGER PRIMARY KEY, Name TEXT);
        CREATE TABLE Track (
            TrackId INTEGER PRIMARY KEY,
            AlbumId INTEGER,
            GenreId INTEGER
        );
        CREATE TABLE InvoiceLine (
            InvoiceLineId INTEGER PRIMARY KEY,
            InvoiceId INTEGER,
            TrackId INTEGER,
            Quantity INTEGER
        );

        INSERT INTO Employee VALUES
            (1,'Alpha','Alice','2019-01-01'),
            (2,'Beta','Bob','2019-01-01');

        INSERT INTO Customer VALUES
            (1,'USA',1),
            (2,'USA',1),
            (3,'Canada',2);

        INSERT INTO Genre VALUES (1,'Rock'),(2,'Jazz');
        INSERT INTO Track VALUES
            (1,10,1),(2,10,1),(3,20,2),(4,20,2);

        -- Customer 1: Jan + Mar. Customer 2: Jan only. Customer 3: Feb + Mar.
        INSERT INTO Invoice VALUES
            (1,1,'2020-01-15','USA',10.0),
            (2,2,'2020-01-20','USA',20.0),
            (3,3,'2020-02-20','Canada',20.0),
            (4,1,'2020-03-10','USA',20.0),
            (5,3,'2020-03-20','Canada',10.0);

        -- Invoice 1 buys the complete two-track Rock album; others are partial.
        INSERT INTO InvoiceLine VALUES
            (1,1,1,1),(2,1,2,1),
            (3,2,1,1),
            (4,3,3,1),
            (5,4,2,1),
            (6,5,4,1);
        """
    )
    return con


def _query(name: str) -> str:
    return (SQL_DIR / name).read_text(encoding="utf-8")


def test_all_query_files_execute_on_fixture():
    con = _fixture_db()
    files = sorted(SQL_DIR.glob("*.sql"))
    assert len(files) == 8
    for path in files:
        con.execute(path.read_text(encoding="utf-8")).fetchall()


def test_agent_report_separates_total_sales_from_portfolio_normalisation():
    con = _fixture_db()
    rows = con.execute(_query("02_sales_agent_performance.sql")).fetchall()
    # Alice manages two customers and leads total revenue: 50 vs Bob's 30.
    assert rows[0][0] == "Alice Alpha"
    assert rows[0][3] == 50.0
    # Bob has the higher revenue/customer: 30 vs Alice's 25.
    by_agent = {row[0]: row for row in rows}
    assert by_agent["Alice Alpha"][4] == 25.0
    assert by_agent["Bob Beta"][4] == 30.0


def test_dense_cohort_query_materialises_zero_activity_months():
    con = _fixture_db()
    rows = con.execute(_query("07_customer_cohorts.sql")).fetchall()
    # Jan cohort has customers 1 and 2. Nobody buys in month 1 (Feb), while
    # customer 1 returns in month 2 (Mar). The zero month must be explicit.
    assert ("2020-01", 0, 2, 2, 100.0) in rows
    assert ("2020-01", 1, 2, 0, 0.0) in rows
    assert ("2020-01", 2, 2, 1, 50.0) in rows


def test_pooled_activity_uses_only_cohorts_eligible_for_each_horizon():
    con = _fixture_db()
    rows = con.execute(_query("08_cohort_activity_summary.sql")).fetchall()
    by_offset = {row[0]: row for row in rows}
    # Offset 1: both Jan (n=2) and Feb (n=1) cohorts are eligible; only the
    # Feb customer buys exactly one month after first purchase -> 1/3 = 33.3%.
    assert by_offset[1] == (1, 2, 3, 1, 33.3)
    # Offset 2: only the Jan cohort has had enough follow-up -> 1/2 = 50%.
    assert by_offset[2] == (2, 1, 2, 1, 50.0)


def test_album_query_identifies_complete_album_purchase():
    con = _fixture_db()
    rows = con.execute(_query("04_album_vs_track.sql")).fetchall()
    result = {purchase_type: (invoices, pct) for purchase_type, invoices, pct in rows}
    assert result["full album"][0] == 1
    assert result["individual tracks"][0] == 4


def test_monthly_revenue_logic_on_fixture():
    con = _fixture_db()
    df = pd.read_sql_query(_query("05_monthly_sales_trend.sql"), con)
    assert df.to_dict("records") == [
        {"month": "2020-01", "revenue": 30.0, "orders": 2},
        {"month": "2020-02", "revenue": 20.0, "orders": 1},
        {"month": "2020-03", "revenue": 30.0, "orders": 2},
    ]


def test_download_validator_requires_chinook_table_set(tmp_path):
    db = tmp_path / "bad.sqlite"
    con = sqlite3.connect(db)
    con.execute("CREATE TABLE Customer (CustomerId INTEGER)")
    con.commit()
    con.close()

    # This pins the schema guard without requiring network access.
    import pytest
    with pytest.raises(RuntimeError, match="missing tables"):
        validate_database(db)
    assert EXPECTED_TABLES - {"Customer"}


def test_download_validator_accepts_minimal_expected_schema(tmp_path):
    db = tmp_path / "chinook_like.sqlite"
    con = sqlite3.connect(db)
    for table in sorted(EXPECTED_TABLES):
        con.execute(f'CREATE TABLE "{table}" (id INTEGER)')
    for table in ("Customer", "Invoice", "InvoiceLine", "Track"):
        con.execute(f'INSERT INTO "{table}" VALUES (1)')
    con.commit()
    con.close()
    validate_database(db)
