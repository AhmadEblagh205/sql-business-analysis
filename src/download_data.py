"""Download and validate the pinned Chinook 1.4.5 SQLite sample database."""
from pathlib import Path
import sqlite3
from urllib.request import urlretrieve

URL = (
    "https://github.com/lerocha/chinook-database/releases/download/"
    "v1.4.5/Chinook_Sqlite.sqlite"
)
DEST = Path(__file__).resolve().parents[1] / "data" / "raw" / "chinook.sqlite"
EXPECTED_TABLES = {
    "Album",
    "Artist",
    "Customer",
    "Employee",
    "Genre",
    "Invoice",
    "InvoiceLine",
    "MediaType",
    "Playlist",
    "PlaylistTrack",
    "Track",
}


def validate_database(path: Path) -> None:
    """Fail loudly if the downloaded file is not a usable Chinook database."""
    con = sqlite3.connect(path)
    try:
        integrity = con.execute("PRAGMA integrity_check").fetchone()[0]
        if integrity != "ok":
            raise RuntimeError(f"SQLite integrity check failed: {integrity}")

        tables = {
            row[0]
            for row in con.execute(
                "SELECT name FROM sqlite_master WHERE type='table'"
            ).fetchall()
        }
        missing = EXPECTED_TABLES - tables
        if missing:
            raise RuntimeError(f"Downloaded database is missing tables: {sorted(missing)}")

        for table in ("Customer", "Invoice", "InvoiceLine", "Track"):
            count = con.execute(f'SELECT COUNT(*) FROM "{table}"').fetchone()[0]
            if count <= 0:
                raise RuntimeError(f"Downloaded database has no rows in {table}")
    finally:
        con.close()


def main() -> Path:
    DEST.parent.mkdir(parents=True, exist_ok=True)
    if not DEST.exists():
        print(f"Downloading Chinook v1.4.5 -> {DEST}")
        urlretrieve(URL, DEST)
        print(f"Downloaded {DEST.stat().st_size / 1e6:.1f} MB")
    else:
        print(f"Already downloaded: {DEST}")

    validate_database(DEST)
    print("Database validation passed.")
    return DEST


if __name__ == "__main__":
    main()
