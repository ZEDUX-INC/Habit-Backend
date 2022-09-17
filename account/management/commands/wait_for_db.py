import time
from typing import Any

from django.core.management import BaseCommand
from django.db import connections
from django.db.utils import OperationalError


class Command(BaseCommand):
    """Django command to pause execution until db is available"""

    def handle(self, *args: list[Any], **options: dict[str, Any]) -> None:

        self.stdout.write("Waiting for database...")
        db_conn = None
        while not db_conn:
            try:
                db_conn = connections["default"]
            except OperationalError:
                self.stdout.write("Database unavailable, waititng 1 second...")
                time.sleep(1)

        self.stdout.write(self.style.SUCCESS("Database available!"))  # type: ignore
