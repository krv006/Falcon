from django.views.generic import TemplateView
from django.contrib.auth import logout
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import redirect, render, get_object_or_404
from django.urls import reverse_lazy
from django.views import View
from django.views.generic import ListView, DetailView, UpdateView, CreateView

from apps.forms import UserRegisterModelForm
from apps.models import Product, Category, Favorite, CartItem, Cart, Address
from apps.tasks import send_to_email
from django.db.models import F, Sum, Q
from apps.models import User


class CategoryMixin:
    def get_context_data(self, *, object_list=None, **kwargs):
        context = super().get_context_data(object_list=object_list, **kwargs)
        context['categories'] = Category.objects.filter()  # TODO Children dib yozish kerak
        return context


class ProductLIstTemplateView(TemplateView):
    template_name = 'apps/product/product-list.html'


# class ProductLIstTemplateView(TemplateView):
#     queryset = Product.objects.order_by('-created_at) bunda oxirgi qoshilganlarini boshda chiqazib beradi
#     template_name = 'ap;ps/product/product-list.html'


class ProductListTemplateView(LoginRequiredMixin, CategoryMixin, ListView):
    template_name = 'apps/product/product-list.html'
    context_object_name = 'products'
    paginate_by = 2

    def get_queryset(self):
        qs = Product.objects.all().order_by('id')
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
        form.save()
        send_to_email.delay('Your account has been created!', form.data['email'])
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

    def get(self, request, *args, **kwargs):
        favourite_items = Favorite.objects.filter(user=request.user)
        # for item in favourite_items: # TODO property ga otkazish kk
        #     item.total_price = item.product.current_price

        context = {
            'favourite_items': favourite_items,
        }
        return render(request, self.template_name, context)


class AddToCartView(LoginRequiredMixin, View):
    def get(self, request, pk, *args, **kwargs):
        product = get_object_or_404(Product, id=pk)
        cart, created = Cart.objects.get_or_create(user=request.user)
        cart_item, created = CartItem.objects.get_or_create(cart=cart, product=product)

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
    queryset = CartItem.objects.all()
    template_name = 'apps/shop/shopping-cart.html'
    context_object_name = 'cart_items'

    # success_url = reverse_lazy('shopping_cart_page') # TODO ishlamaydi

    def get_queryset(self):
        return super().get_queryset().filter(cart__user=self.request.user)

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
    fields = 'full_name',  'phone', 'city', 'street', 'zip_code'
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


class CheckoutView(CategoryMixin, TemplateView):
    template_name = 'apps/shop/checkout.html'
