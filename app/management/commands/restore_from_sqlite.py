import os
import tarfile
import tempfile

from django.conf import settings
from django.core.management import call_command
from django.core.management.base import BaseCommand, CommandError


class Command(BaseCommand):
    help = "Restore data from a SQLite backup into PostgreSQL and extract media files."

    def add_arguments(self, parser):
        parser.add_argument("sqlite_path", help="Path to the db.sqlite3 backup file")
        parser.add_argument(
            "--media-tar",
            help="Path to a .tar.gz containing the media folder (optional)",
        )

    def handle(self, *args, **options):
        sqlite_path = options["sqlite_path"]
        media_tar = options.get("media_tar")

        if not os.path.exists(sqlite_path):
            raise CommandError(f"SQLite file not found: {sqlite_path}")

        self.stdout.write("Step 1/3 — Exporting data from SQLite...")
        fixture_path = self._dump_sqlite(sqlite_path)

        self.stdout.write("Step 2/3 — Loading data into PostgreSQL (overwriting)...")
        self._load_fixture(fixture_path)
        os.unlink(fixture_path)

        if media_tar:
            self.stdout.write("Step 3/3 — Extracting media files...")
            self._extract_media(media_tar)
        else:
            self.stdout.write("Step 3/3 — Skipped (no --media-tar provided).")

        self.stdout.write(self.style.SUCCESS("Restore complete."))

    def _dump_sqlite(self, sqlite_path: str) -> str:
        tmp = tempfile.NamedTemporaryFile(
            delete=False, suffix=".json", mode="w", encoding="utf-8"
        )
        tmp.close()

        import django
        from django.test.utils import override_settings

        sqlite_db = {
            "default": {
                "ENGINE": "django.db.backends.sqlite3",
                "NAME": sqlite_path,
            }
        }
        with override_settings(DATABASES=sqlite_db):
            django.db.connections.close_all()
            call_command(
                "dumpdata",
                "--natural-foreign",
                "--natural-primary",
                "--exclude=auth.permission",
                "--exclude=contenttypes",
                output=tmp.name,
                verbosity=0,
            )
            django.db.connections.close_all()

        self.stdout.write(f"  Fixture written to {tmp.name}")
        return tmp.name

    def _load_fixture(self, fixture_path: str) -> None:
        # Clear existing data except migrations table
        from django.db import connection

        with connection.cursor() as cursor:
            cursor.execute("SET session_replication_role = replica;")
            tables = [
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
            ]
            for table in tables:
                cursor.execute(f"TRUNCATE TABLE {table} RESTART IDENTITY CASCADE;")
            cursor.execute("SET session_replication_role = DEFAULT;")

        call_command("loaddata", fixture_path, verbosity=1)

    def _extract_media(self, media_tar: str) -> None:
        media_root = settings.MEDIA_ROOT
        os.makedirs(media_root, exist_ok=True)

        with tarfile.open(media_tar) as tar:
            tar.extractall(path=media_root, filter="data")
            count = len(tar.getnames())

        self.stdout.write(f"  {count} files extracted to {media_root}")
