from django.db import models
from django.db.models import Model, JSONField
from django.utils.text import slugify
from django_ckeditor_5.fields import CKEditor5Field
from mptt.models import MPTTModel, TreeForeignKey
from django.utils.timezone import now

from datetime import timedelta


class Category(MPTTModel):
    name = models.CharField(max_length=255, unique=True)
    slug = models.SlugField(max_length=255, unique=True, editable=False)
    parent = TreeForeignKey('self', on_delete=models.CASCADE, null=True, blank=True, related_name='children')

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

    class MPTTMeta:
        order_insertion_by = ['name']

    def __str__(self):
        return self.name


class Product(Model):
    title = models.CharField(max_length=355)
    price = models.DecimalField(max_digits=7, decimal_places=2)
    price_percentage = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    shopping_cost = models.DecimalField(default=0, max_digits=7, decimal_places=2)
    quantity = models.PositiveIntegerField(default=0)
    description = JSONField()
    short_description = CKEditor5Field()
    long_description = CKEditor5Field()
    category = models.ForeignKey('apps.Category', models.CASCADE)
    tags = models.ManyToManyField('apps.Tag', related_name='tag')
    updated_at = models.DateTimeField(auto_now_add=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title

    @property
    def new_price(self):
        return self.price * (100 - self.price_percentage) // 100

    @property
    def is_new(self) -> bool:
        return self.created_at >= now() - timedelta(days=7)


class ImageProduct(Model):
    image = models.ImageField(upload_to='products/%Y/%m/%d/')
    product = models.ForeignKey('apps.Product', models.CASCADE, related_name='images')


class Tag(models.Model):
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


class Review(Model):
    name = models.CharField(max_length=255)
    email = models.EmailField(max_length=255, null=True, blank=True)
    description = models.TextField()
    comment_status = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    product = models.ForeignKey('apps.Product', models.CASCADE, related_name='reviw')

    def __str__(self):
        return self.name
