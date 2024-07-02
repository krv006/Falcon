from django.urls import path
from .views import ProductLIstTemplateView, ProductListTemplateView, ProductDetailTemplateView

urlpatterns = [
    # path('rv/', ProductLIstTemplateView.as_view(), name='product_list'),
    path('', ProductListTemplateView.as_view(), name='product_list'),
    path('product/detail/<int:pk>/', ProductDetailTemplateView.as_view(), name='product_detail'),
]
