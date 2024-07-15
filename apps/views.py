from django.contrib.auth import logout
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import F, Sum, Q, Prefetch
from django.shortcuts import redirect, get_object_or_404
from django.urls import reverse_lazy
from django.views import View
from django.views.generic import ListView, DetailView, UpdateView, CreateView
from django.core.cache import cache

from apps.forms import UserRegisterModelForm
from apps.models import Product, Category, Favorite, CartItem, Address, ImageProduct
from apps.models import User


class CategoryMixin:
    def get_context_data(self, *, object_list=None, **kwargs):
        context = super().get_context_data(object_list=object_list, **kwargs)
        context['categories'] = Category.objects.filter()  # TODO Children dib yozish kerak
        return context


class ProductListView(CategoryMixin, ListView):
    queryset = Product.objects.select_related('category').prefetch_related('images').order_by('id')
    template_name = 'apps/product/product-list.html'
    context_object_name = 'products'
    paginate_by = 10

    def get_queryset(self):

        if cache.get('product_list'):
            return cache.get('product_list')
        qs = super().get_queryset()
        cache.set('product_list', qs, timeout=7200)

        category_slug = self.request.GET.get('category')
        if category_slug:
            qs = qs.filter(category__slug=category_slug)
        if tags_slug := self.request.GET.get('tag'):
            qs = qs.filter(tags__slug=tags_slug)
        if ordering := self.request.GET.get('ordering'):
            qs = qs.order_by(ordering)
        # search = self.request.GET.get('search')
        if search := self.request.GET.get('search'):
            qs = qs.filter(Q(title__icontains=search) | Q(description__icontains=search))
        return qs




class ProductDetailTemplateView(CategoryMixin, DetailView):
    model = Product
    template_name = 'apps/product/product-details.html'
    context_object_name = 'product'


class RegisterCreateView(CreateView):
    queryset = User.objects.all()
    template_name = 'apps/auth/register.html'
    form_class = UserRegisterModelForm
    success_url = reverse_lazy('product_list_page')

    def form_valid(self, form):
        # send_to_email.delay('Your account has been created!', form.data['email'])
        form.save()
        return super().form_valid(form)

    def form_invalid(self, form):
        return super().form_invalid(form)


class SettingsUpdateView(CategoryMixin, LoginRequiredMixin, UpdateView):
    queryset = User.objects.all()
    fields = 'first_name', 'last_name'
    template_name = 'apps/auth/settings.html'
    success_url = reverse_lazy('settings_page')

    def get_object(self, queryset=None):
        return self.request.user


class FavouriteView(View):
    template_name = 'apps/shop/favourite.html'

    def get(self, request, pk, *args, **kwargs):
        obj, created = Favorite.objects.get_or_create(user=request.user, product_id=pk)
        if not created:
            obj.delete()
        return redirect('product_detail', pk=pk)


class AddToCartView(LoginRequiredMixin, View):
    def get(self, request, pk, *args, **kwargs):
        product = get_object_or_404(Product, id=pk)
        cart_item, created = CartItem.objects.get_or_create(user=request.user, product=product)

        if not created:
            cart_item.quantity += 1
            cart_item.save()

        return redirect('shopping_cart_page')


class CustomLogoutView(View):
    template_name = 'apps/auth/login.html'  # TODO ishlamaydi

    def get(self, request, *args, **kwargs):
        logout(request)
        return redirect('product_list_page')


class CartListView(CategoryMixin, ListView):
    # queryset = Category.objects.prefetch_related('product') # 1 -> N
    queryset = CartItem.objects.select_related('product')  # N -> 1
    template_name = 'apps/shop/shopping-cart.html'
    context_object_name = 'cart_items'

    def get_context_data(self, *, object_list=None, **kwargs):
        ctx = super().get_context_data(object_list=object_list, **kwargs)
        qs = self.get_queryset()

        ctx.update(
            **qs.aggregate(
                total_sum=Sum(F('quantity') * F('product__price') * (100 - F('product__price_percentage')) / 100),
                total_count=Sum(F('quantity'))
            )
        )
        return ctx


class CartItemDeleteView(CategoryMixin, View):

    def get(self, request, pk, *args, **kwargs):
        cart_item = get_object_or_404(CartItem, pk=pk, cart__user=self.request.user)
        cart_item.delete()
        return redirect('shopping_cart_page')


class AddressCreateView(CategoryMixin, CreateView):
    model = Address
    template_name = 'apps/address/address_create.html'
    fields = 'full_name', 'phone', 'city', 'street', 'zip_code'
    context_object_name = 'create_address'

    def form_valid(self, form):
        form.instance.user = self.request.user
        return super().form_valid(form)


class AddressUpdateView(CategoryMixin, UpdateView):
    model = Address
    template_name = 'apps/address/edit.html'
    fields = ['city', 'street', 'zip_code', 'phone']
    success_url = reverse_lazy('checkout_page')
    context_object_name = 'address'


class CheckoutListView(LoginRequiredMixin, CategoryMixin, ListView):
    queryset = CartItem.objects.all()
    template_name = 'apps/shop/checkout.html'
    context_object_name = 'cart_items'

    def get_queryset(self):
        return super().get_queryset().filter(user=self.request.user)
