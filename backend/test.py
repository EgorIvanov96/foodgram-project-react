import json
from reviews.models import Ingredient

def import_data_from_json(file_path):
    with open(file_path, 'r') as file:
        data = json.load(file)

    for item in data:
        Ingredient.objects.create(
            name=item['name'],
            measurement_unit=item['measurement_unit']
        )

# Пример использования
file_path = ingredients.json
import_data_from_json(file_path)
