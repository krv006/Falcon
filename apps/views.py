from itertools import product

from django.shortcuts import render
from django.views.generic import TemplateView, DetailView, ListView

from apps.models import Product, Category


class ProductLIstTemplateView(TemplateView):
    template_name = 'apps/product/product-list.html'


# class ProductLIstTemplateView(TemplateView):
#     queryset = Product.objects.order_by('-created_at) bunda oxirgi qoshilganlarini boshda chiqazib beradi
#     template_name = 'apps/product/product-list.html'


class ProductListTemplateView(ListView):
    queryset = Product.objects.all()
    template_name = 'apps/product/product-list.html'
    context_object_name = 'products'
    paginate_by = 2

    def get_queryset(self):
        qs = super().get_queryset()
        category_slug = self.request.GET.get('category')
        if category_slug:
            qs = qs.filter(category__slug=category_slug)
        if ordering := self.request.GET.get('ordering'):
            qs = qs.order_by(ordering)
        search = self.request.GET.get('search')
        if search:
            qs = qs.filter(title__icontains=search)
        return qs

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super().get_context_data(object_list=object_list, **kwargs)
        context['categories'] = Category.objects.all()
        return context


class ProductDetailTemplateView(DetailView):
    model = Product
    template_name = 'apps/product/product-details.html'
    context_object_name = 'product'

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super().get_context_data(object_list=object_list, **kwargs)
        context['categories'] = Category.objects.all()
        return context
