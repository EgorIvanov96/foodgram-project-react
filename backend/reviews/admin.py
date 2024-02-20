from django.contrib import admin

from .models import Tag, Ingredient, Recipes, IngredientRecipes


class TagAdmin(admin.ModelAdmin):
    prepopulated_fields = {'slug': ('name',)}


"""class IngredientInLine(admin.TabularInline):
    model = Recipes.ingredients.through


class RecipesAdmin(admin.ModelAdmin):
    inlines = [IngredientInLine]"""


class IngredientRecipesLine(admin.TabularInline):
    model = IngredientRecipes
    extra = 1


class RecipesAdmin(admin.ModelAdmin):
    inlines = (IngredientRecipesLine,)


class IngredientRecipesAdmin(admin.ModelAdmin):
    inlines = (IngredientRecipesLine,)


admin.site.register(Tag, TagAdmin)
admin.site.register(Ingredient)
# admin.site.register(Recipes, RecipesAdmin)
admin.site.register(Recipes)
# admin.site.register(IngredientRecipes, IngredientRecipesAdmin)
admin.site.register(IngredientRecipes)
admin.site.empty_value_display = 'Не задано'
