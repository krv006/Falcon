from django.contrib import admin
from apps.models import ImageProduct, Product, Category, Tag, Review


class ImageProductStackedInline(admin.StackedInline):
    model = ImageProduct
    extra = 1
    max_num = 5
    min_num = 1


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    pass


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
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
