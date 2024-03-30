import csv

from django.core.management import BaseCommand

from reviews.models import Ingredient, Tag


class Command(BaseCommand):
    def import_ingredients(self):
        try:
            with open('./data/ingredients.csv', encoding='utf-8') as csvfile:
                reader = csv.reader(csvfile)
                for row in reader:
                    name, measurement_unit = row[:2]
                    Ingredient.objects.get_or_create(
                        name=name, measurement_unit=measurement_unit
                    )
        except FileNotFoundError:
            print(
                'Файл не найден. Убедитесь, что путь к файлу верный.'
            )

    def import_tags(self):
        try:
            with open('./data/tags.csv', encoding='utf-8') as csvfile:
                reader = csv.reader(csvfile)
                for row in reader:
                    name, color, slug = row[:3]
                    Tag.objects.get_or_create(
                        name=name,
                        color=color,
                        slug=slug
                    )
        except FileExistsError:
            print(
                'Файл не найден. Убедитесь, что путь к файлу верный.'
            )

    def handle(self, *args, **options):
        self.import_ingredients()
        self.import_tags()
        self.stdout.write(self.style.SUCCESS('Данные импортированы'))
