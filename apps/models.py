from datetime import timedelta

from django.contrib.auth.base_user import AbstractBaseUser
from django.contrib.auth.models import AbstractUser
from django.db.models import Model, JSONField, TextChoices, DateField, CharField, CASCADE, \
    PositiveIntegerField, ForeignKey, DateTimeField, TextField, EmailField, SlugField, ManyToManyField, DecimalField, \
    ImageField, IntegerField
from django.utils.text import slugify
from django.utils.timezone import now
from django_ckeditor_5.fields import CKEditor5Field
from mptt.models import MPTTModel, TreeForeignKey


# class CreatedBaseModel(Model):
#     updated_at = DateTimeField(auto_now=True)
#     created_at = DateTimeField(auto_now_add=True)
#
#     class Meta:
#         abstract = True


class User(AbstractUser):
    @property
    def cart_count(self):
        return self.cart_items.count()


class Category(MPTTModel):
    name = CharField(max_length=255, unique=True)
    slug = SlugField(max_length=255, unique=True, editable=False)
    parent = TreeForeignKey('self', on_delete=CASCADE, null=True, blank=True, related_name='children')

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
    title = CharField(max_length=355)
    price = DecimalField(max_digits=7, decimal_places=2)
    price_percentage = DecimalField(max_digits=5, decimal_places=2, default=0)
    shopping_cost = DecimalField(default=0, max_digits=7, decimal_places=2)
    quantity = PositiveIntegerField(default=0)
    description = JSONField()
    short_description = CKEditor5Field()
    long_description = CKEditor5Field()
    category = ForeignKey('apps.Category', CASCADE)
    tags = ManyToManyField('apps.Tag', related_name='tag')
    updated_at = DateTimeField(auto_now_add=True)
    created_at = DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title

    @property
    def new_price(self):
        return self.price * (100 - self.price_percentage) // 100

    @property
    def is_new(self) -> bool:
        return self.created_at >= now() - timedelta(days=7)


class ImageProduct(Model):
    image = ImageField(upload_to='products/%Y/%m/%d/')
    product = ForeignKey('apps.Product', CASCADE, related_name='images')


class Tag(Model):
    name = CharField(max_length=255)
    slug = SlugField(max_length=255, unique=True, editable=False)

    def save(self, force_insert=False, force_update=False, using=None, update_fields=None):
        if not self.slug:
            self.slug = slugify(self.name)
            unique = self.slug
            num = 1
            while Tag.objects.filter(slug=unique).exists():
                unique = f'{self.slug}-{num}'
                num += 1
            self.slug = unique
        super().save(force_insert, force_update, using, update_fields)


class Review(Model):
    name = CharField(max_length=255)
    email = EmailField(max_length=255, null=True, blank=True)
    description = TextField()
    comment_status = TextField()
    created_at = DateTimeField(auto_now_add=True)
    product = ForeignKey('apps.Product', CASCADE, related_name='reviw')

    def __str__(self):
        return self.name


class Favorite(Model):
    user = ForeignKey(User, CASCADE)
    product = ForeignKey('apps.Product', CASCADE)
    created_at = DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user', 'product')


class CartItem(Model):
    product = ForeignKey('apps.Product', CASCADE)
    user = ForeignKey('apps.User', CASCADE, related_name='cart_items')
    quantity = PositiveIntegerField(default=1)

    def __str__(self):
        return f"{self.quantity} x {self.product.title}"

    @property
    def amount(self):
        return self.quantity * self.product.new_price

    @property
    def total(self):
        return self.amount - self.product.shopping_cost


class Order(Model):
    class StatusMethod(TextChoices):
        COMPLETED = 'completed', 'Completed'
        PROCESSING = 'processing', 'Processing'
        ON_HOLD = 'on hold', 'On Hold'
        PENDING = 'pending', 'Pending'

    class PaymentMethod(TextChoices):
        PAYPAL = 'paypal', 'Paypal'
        CREDIT_CARD = 'credit_card', 'Credit_card'

    status = CharField(max_length=255, choices=StatusMethod)
    payment_method = CharField(max_length=255, choices=PaymentMethod)
    address = ForeignKey('apps.Address', CASCADE)
    owner = ForeignKey('apps.User', CASCADE, related_name='orders')
    created_at = DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'Order {self.id} - {self.status}'


class Address(Model):
    user = ForeignKey('apps.User', CASCADE)
    full_name = CharField(max_length=255)
    street = CharField(max_length=255)
    zip_code = PositiveIntegerField()
    city = CharField(max_length=255)
    phone = CharField(max_length=255)


class OrderItem(Model):
    product = ForeignKey('apps.Product', CASCADE)
    order = ForeignKey('apps.Order', CASCADE, related_name='items')
    quantity = PositiveIntegerField(default=0)


class CreditCard(Model):
    order = ForeignKey('apps.Order', CASCADE)
    number = CharField(max_length=255)
    cvv = CharField(max_length=255)
    expire_date = DateField()
    owner = ForeignKey('apps.User', CASCADE)


class SiteSettings(Model):
    tax = PositiveIntegerField()
