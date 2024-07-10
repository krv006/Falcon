from django.contrib import admin
from mptt.admin import DraggableMPTTAdmin

from apps.models import ImageProduct, Product, Category, Tag, Review
from import_export.admin import ImportExportModelAdmin

from .models import User


class ImageProductStackedInline(admin.StackedInline):
    model = ImageProduct
    extra = 1
    max_num = 5
    min_num = 1


@admin.register(Category)
class CategoryAdmin(DraggableMPTTAdmin, ImportExportModelAdmin):
    pass


# admin.site.register(User)

@admin.register(User)
class UserAdmin(ImportExportModelAdmin):
    pass


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ('id', 'title', 'price')
    inlines = ImageProductStackedInline,


@admin.register(ImageProduct)
class ImageProductAdmin(admin.ModelAdmin):
    pass


@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    pass


@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    pass
