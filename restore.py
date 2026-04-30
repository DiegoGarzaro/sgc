#!/usr/bin/env python
"""
Restore SQLite data into PostgreSQL.
Usage: python restore.py <path-to-db.sqlite3>
"""

import os
import sys
import tempfile

import django

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "app.settings")


def main():
    if len(sys.argv) < 2:
        print("Usage: python restore.py <path-to-db.sqlite3>")
        sys.exit(1)

    sqlite_path = os.path.abspath(sys.argv[1])
    if not os.path.exists(sqlite_path):
        print(f"File not found: {sqlite_path}")
        sys.exit(1)

    django.setup()

    from django.apps import apps
    from django.conf import settings
    from django.core.management import call_command
    from django.core.management.color import no_style
    from django.db import connections

    # Register the SQLite backup as a second DB alias so we can dump from it
    # without disturbing the live `default` connection (PostgreSQL).
    settings.DATABASES["sqlite_source"] = {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": sqlite_path,
        "ATOMIC_REQUESTS": False,
        "AUTOCOMMIT": True,
        "CONN_MAX_AGE": 0,
        "CONN_HEALTH_CHECKS": False,
        "OPTIONS": {},
        "TIME_ZONE": None,
        "USER": "",
        "PASSWORD": "",
        "HOST": "",
        "PORT": "",
        "TEST": {},
    }
    # Invalidate any cached settings on the connection handler so the new alias
    # is picked up on next access.
    connections.__dict__.pop("settings", None)
    connections.__dict__.pop("databases", None)

    print(f"Reading from: {sqlite_path}")

    fixture = tempfile.NamedTemporaryFile(
        delete=False, suffix=".json", mode="w", encoding="utf-8"
    )
    fixture.close()

    try:
        # Step 1 — dump from SQLite
        call_command(
            "dumpdata",
            "--natural-foreign",
            "--natural-primary",
            "--exclude=auth.permission",
            "--exclude=contenttypes",
            "--database=sqlite_source",
            output=fixture.name,
            verbosity=1,
        )
        size = os.path.getsize(fixture.name)
        print(f"Exported {size} bytes to {fixture.name}")
        if size < 10:
            print("ERROR: fixture file is empty — nothing to load.")
            sys.exit(1)

        # Step 2 — wipe PostgreSQL
        print("Clearing PostgreSQL tables...")
        call_command("flush", "--no-input", "--database=default", verbosity=0)

        # Step 3 — load into PostgreSQL
        print("Loading data into PostgreSQL...")
        call_command("loaddata", fixture.name, "--database=default", verbosity=1)

        # Step 4 — fix sequences. loaddata inserts rows with explicit PKs but
        # leaves PostgreSQL sequences at their initial value, so the next insert
        # collides. Reset every sequence to MAX(pk)+1.
        print("Resetting PostgreSQL sequences...")
        conn = connections["default"]
        sequence_sql = conn.ops.sequence_reset_sql(no_style(), apps.get_models())
        with conn.cursor() as cursor:
            for sql in sequence_sql:
                cursor.execute(sql)
        print(f"  {len(sequence_sql)} sequences reset.")

    finally:
        if os.path.exists(fixture.name):
            os.remove(fixture.name)

    print("Done.")


if __name__ == "__main__":
    main()
