import os
import tarfile
import tempfile

from django.apps import apps
from django.conf import settings
from django.core.management import call_command
from django.core.management.base import BaseCommand, CommandError
from django.core.management.color import no_style


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
        self._flush_target_database()
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
        from django.db import connections

        call_command("loaddata", fixture_path, verbosity=1)

        # loaddata preserves explicit primary keys but does not advance PostgreSQL
        # sequences, so reset them to avoid duplicate-key errors on Railway.
        connection = connections["default"]
        sequence_sql = connection.ops.sequence_reset_sql(no_style(), apps.get_models())
        with connection.cursor() as cursor:
            for sql in sequence_sql:
                cursor.execute(sql)

    def _flush_target_database(self) -> None:
        call_command("flush", "--no-input", "--database=default", verbosity=0)

    def _extract_media(self, media_tar: str) -> None:
        media_root = settings.MEDIA_ROOT
        os.makedirs(media_root, exist_ok=True)

        with tarfile.open(media_tar) as tar:
            tar.extractall(path=media_root, filter="data")
            count = len(tar.getnames())

        self.stdout.write(f"  {count} files extracted to {media_root}")
