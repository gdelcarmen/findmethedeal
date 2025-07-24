"""SQLite helper functions for the niches table.

The orchestrator uses a lightweight SQLite database to remember which
niches have already been covered.  The table schema closely follows
the reference design:

```
CREATE TABLE niches (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  slug TEXT UNIQUE,
  keyword_seed TEXT,
  site_url TEXT,
  status TEXT  -- planned | published | refresh_due
);
```

We store `keyword_seed` as a JSON‑encoded list of strings so that
multiple seed keywords can be recorded per niche.  If you prefer to
use PostgreSQL or another database engine, the same helper functions
can be adapted accordingly.
"""

from __future__ import annotations

import json
import sqlite3
from pathlib import Path
from typing import Iterable, Optional

# Path to the SQLite database file.  It lives alongside this module.
DB_PATH = Path(__file__).resolve().parent / "niches.db"


def get_connection() -> sqlite3.Connection:
    """Create a connection to the SQLite database.

    Returns:
        sqlite3.Connection: A connection object.
    """
    return sqlite3.connect(DB_PATH)


def init_db() -> None:
    """Create the `niches` table if it does not already exist."""
    conn = get_connection()
    try:
        with conn:
            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS niches (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    slug TEXT UNIQUE,
                    keyword_seed TEXT,
                    site_url TEXT,
                    status TEXT
                )
                """
            )
    finally:
        conn.close()


def niche_exists(slug: str) -> bool:
    """Check whether a niche with the given slug already exists.

    Args:
        slug (str): The slug identifying the niche.

    Returns:
        bool: True if the niche is present, False otherwise.
    """
    conn = get_connection()
    try:
        cur = conn.execute("SELECT 1 FROM niches WHERE slug = ?", (slug,))
        return cur.fetchone() is not None
    finally:
        conn.close()


def insert_niche(slug: str, keyword_seed: Iterable[str], site_url: Optional[str] = None,
                 status: str = "planned") -> None:
    """Insert a new niche into the database.

    Args:
        slug (str): The unique slug for the niche.
        keyword_seed (Iterable[str]): Seed keywords used to generate the site.
        site_url (Optional[str], optional): The URL where the site will be hosted.
        status (str, optional): Initial status for the niche. Defaults to "planned".
    """
    conn = get_connection()
    try:
        with conn:
            conn.execute(
                "INSERT INTO niches (slug, keyword_seed, site_url, status) VALUES (?, ?, ?, ?)",
                (slug, json.dumps(list(keyword_seed)), site_url, status),
            )
    finally:
        conn.close()


def update_niche_status(slug: str, status: str) -> None:
    """Update the status of an existing niche.

    Args:
        slug (str): The slug identifying the niche.
        status (str): The new status (e.g. 'published', 'refresh_due').
    """
    conn = get_connection()
    try:
        with conn:
            conn.execute("UPDATE niches SET status = ? WHERE slug = ?", (status, slug))
    finally:
        conn.close()