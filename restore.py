#!/usr/bin/env python
"""
Restore SQLite data into PostgreSQL.
Usage: python restore.py <path-to-db.sqlite3>
"""

import os
import sys

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

    from django.core.management import call_command
    from django.db import connections
    from django.test.utils import override_settings

    print(f"Reading from: {sqlite_path}")

    # Step 1 — dump from SQLite
    tmp = "/tmp/restore_data.json"
    with override_settings(
        DATABASES={
            "default": {
                "ENGINE": "django.db.backends.sqlite3",
                "NAME": sqlite_path,
            }
        }
    ):
        connections.close_all()
        call_command(
            "dumpdata",
            "--natural-foreign",
            "--natural-primary",
            "--exclude=auth.permission",
            "--exclude=contenttypes",
            output=tmp,
            verbosity=0,
        )
        connections.close_all()

    print(f"Exported to {tmp}")

    # Step 2 — clear PostgreSQL and reload
    print("Clearing PostgreSQL tables...")
    call_command("flush", "--no-input", verbosity=0)

    print("Loading data into PostgreSQL...")
    call_command("loaddata", tmp, verbosity=1)

    os.remove(tmp)
    print("Done.")


if __name__ == "__main__":
    main()
