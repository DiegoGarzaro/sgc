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

    # Boot Django with PostgreSQL (from environment DATABASE_URL)
    django.setup()

    from django.core.management import call_command
    from django.db import connections
    from django.test.utils import override_settings

    print(f"Reading from: {sqlite_path}")

    # Step 1 — dump data from SQLite to a temp file
    tmp = "/tmp/restore_data.json"
    sqlite_settings = {
        "default": {
            "ENGINE": "django.db.backends.sqlite3",
            "NAME": sqlite_path,
        }
    }

    with override_settings(DATABASES=sqlite_settings):
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

    # Step 2 — wipe PostgreSQL tables and reload
    from django.db import connection

    print("Clearing PostgreSQL tables...")
    with connection.cursor() as cursor:
        cursor.execute("SET session_replication_role = replica;")
        for table in [
            "social_django_usersocialauth",
            "social_django_nonce",
            "social_django_association",
            "social_django_code",
            "social_django_partial",
            "components_component_equivalents",
            "components_component",
            "brands_brand",
            "categories_category",
            "sub_categories_subcategory",
            "packages_package",
            "suppliers_supplier",
            "products_product",
            "auth_user_groups",
            "auth_user_user_permissions",
            "auth_user",
            "auth_group_permissions",
            "auth_group",
        ]:
            cursor.execute(f"TRUNCATE TABLE {table} RESTART IDENTITY CASCADE;")
        cursor.execute("SET session_replication_role = DEFAULT;")

    print("Loading data into PostgreSQL...")
    call_command("loaddata", tmp, verbosity=1)

    os.remove(tmp)
    print("Done.")


if __name__ == "__main__":
    main()
