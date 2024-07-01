from django.db import models
from django.db.models import Model, JSONField
from django.utils.text import slugify
from django_ckeditor_5.fields import CKEditor5Field


class Category(Model):
    name = models.CharField(max_length=255)
    slug = models.SlugField(max_length=255, unique=True, editable=False)

    def save(self, force_insert=False, force_update=False, using=None, update_fields=None):
        if not self.slug:
            self.slug = slugify(self.name)
            unique = self.slug
            num = 1
            while Category.objects.filter(slug=unique).exists():
                unique = f'{self.slug}-{num}'
                num += 1
            self.slug = unique
        super().save(force_insert, force_update, using, update_fields)

    def __str__(self):
        return self.name


class Product(Model):
    title = models.CharField(max_length=355)
    price = models.DecimalField(max_digits=7, decimal_places=2)
    price_percentage = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    shopping_cost = models.DecimalField(max_digits=7, decimal_places=2)
    quantity = models.PositiveIntegerField()
    description = JSONField()
    short_description = models.TextField(null=True, blank=True)
    long_description = models.TextField(null=True, blank=True)
    category = models.ForeignKey('apps.Category', models.CASCADE)
    tags = models.ManyToManyField('apps.Tag', related_name='tag')
    update_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.title

    @property
    def new_price(self):
        return self.price * (100 - self.price_percentage) // 100


class ImageProduct(Model):
    image = models.ImageField(upload_to='products/%Y/%m/%d/')
    product = models.ForeignKey('apps.Product', models.CASCADE, related_name='images')


class Tag(models.Model):
    tag_name = models.CharField(max_length=255)


class Review(Model):
    name = models.CharField(max_length=255)
    email = models.EmailField(max_length=255, null=True, blank=True)
    description = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    product = models.ForeignKey('apps.Product', models.CASCADE, related_name='reviw')

    def __str__(self):
        return self.name
