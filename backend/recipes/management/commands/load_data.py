from csv import reader

from django.core.management.base import BaseCommand
from django.db.utils import IntegrityError

from recipes.models import Ingridient


class Command(BaseCommand):
    help = "load ingredients data to DB"

    def handle(self, *args, **options):
        with open("recipes/data/ingredients.csv", encoding="utf-8") as f:
            my_reader = reader(f)
            for row in my_reader:
                name, measurement_unit = row
                try:
                    Ingridient.objects.get_or_create(
                        name=name, measurement_unit=measurement_unit
                    )
                except IntegrityError:
                    print(f"{name} уже есть в БД!")
