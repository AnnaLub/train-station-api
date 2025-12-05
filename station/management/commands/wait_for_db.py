import time

from django.core.management.base import BaseCommand
from django.db import connections
from django.db.utils import OperationalError


class Command(BaseCommand):
    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS(
            "Waiting for database connection..."))
        db_connection = connections["default"]
        while not db_connection:
            try:
                db_connection = connections["default"].cursor()
            except OperationalError:
                self.stdout.write(self.style.ERROR(
                    "Database unavailable, waiting for 3 seconds..."))
                time.sleep(3)
        self.stdout.write(self.style.SUCCESS(
            "Database connection established!"))
