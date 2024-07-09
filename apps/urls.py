from django.contrib.auth.views import LoginView
from django.urls import path
from .views import ProductListTemplateView, ProductDetailTemplateView, RegisterCreateView, \
    SettingsUpdateView, LogoutView

urlpatterns = [
    # path('rv/', ProductLIstTemplateView.as_view(), name='product_list'),
    path('', ProductListTemplateView.as_view(), name='product_list_page'),
    path('product-detail/<int:pk>/', ProductDetailTemplateView.as_view(), name='product_detail'),

    path('settings', SettingsUpdateView.as_view(), name='settings_page'),
    path('register', RegisterCreateView.as_view(), name='register_page'),
    path('login', LoginView.as_view(
        template_name='apps/aouth/login.html',
        redirect_authenticated_user=True,
        next_page='product_list_page'
    ), name='login_page'),
    path('logout', LogoutView.as_view(), name='logout_page'),
]
