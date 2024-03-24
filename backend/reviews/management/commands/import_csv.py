import csv

from django.core.management import BaseCommand

from reviews.models import Ingredient


class Command(BaseCommand):
    def import_ingredients(self):
        with open(
            './data/ingredients.csv', encoding='utf-8'
        ) as csvfile:
            reader = csv.DictReader(csvfile)
            for row in reader:
                name = row['name']
                measurement_unit = row['measurement_unit']
                Ingredient.objects.create(
                    name=name, measurement_unit=measurement_unit
                )

    def handle(self, *args, **options):
        self.import_ingredients()
        self.stdout.write(self.style.SUCCESS('Данные импортированы'))
