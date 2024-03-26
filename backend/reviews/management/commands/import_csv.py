import csv

from django.core.management import BaseCommand

from reviews.models import Ingredient


class Command(BaseCommand):
    def import_ingredients(self):
        with open('./data/ingredients.csv', encoding='utf-8') as csvfile:
            reader = csv.reader(csvfile)
            for row in reader:
                Ingredient.objects.create(
                    name=row[0], measurement_unit=row[1]
                )

    def handle(self, *args, **options):
        self.import_ingredients()
        self.stdout.write(self.style.SUCCESS('Данные импортированы'))
