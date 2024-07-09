from django.views.generic import TemplateView
from django.contrib.auth import logout
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.models import User
from django.shortcuts import redirect
from django.urls import reverse_lazy
from django.views import View
from django.views.generic import ListView, DetailView, UpdateView, CreateView

from apps.forms import UserRegisterModelForm
from apps.models import Product, Category
from apps.tasks import send_to_email


class CategoryMixin:
    def get_context_data(self, *, object_list=None, **kwargs):
        context = super().get_context_data(object_list=object_list, **kwargs)
        context['categories'] = Category.objects.all()
        return context


class ProductLIstTemplateView(TemplateView):
    template_name = 'apps/product/product-list.html'


# class ProductLIstTemplateView(TemplateView):
#     queryset = Product.objects.order_by('-created_at) bunda oxirgi qoshilganlarini boshda chiqazib beradi
#     template_name = 'apps/product/product-list.html'


class ProductListTemplateView(CategoryMixin, ListView):
    template_name = 'apps/product/product-list.html'
    context_object_name = 'products'
    paginate_by = 2

    def get_queryset(self):
        qs = Product.objects.all().order_by('id')
        category_slug = self.request.GET.get('category')
        if category_slug:
            qs = qs.filter(category__slug=category_slug)
        if ordering := self.request.GET.get('ordering'):
            qs = qs.order_by(ordering)
        search = self.request.GET.get('search')
        if search:
            qs = qs.filter(title__icontains=search)
        return qs


class ProductDetailTemplateView(CategoryMixin, DetailView):
    model = Product
    template_name = 'apps/product/product-details.html'
    context_object_name = 'product'


class RegisterCreateView(CreateView):
    queryset = User.objects.all()
    template_name = 'apps/aouth/register.html'
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
    template_name = 'apps/aouth/settings.html'
    success_url = reverse_lazy('settings_page')

    def get_object(self, queryset=None):
        return self.request.user


# class CustomLoginView(LoginView):
#     template_name = 'apps/auth/login.html'
#     redirect_authenticated_user = True
#     next_page = reverse_lazy('product_list_page')


class LogoutView(View):

    def get(self, request, *args, **kwargs):
        logout(request)
        return redirect('product_list_page')
