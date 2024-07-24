from django.contrib.auth.views import LoginView
from django.urls import path
from .views import ProductListView, ProductDetailTemplateView, RegisterCreateView, \
    SettingsUpdateView, FavouriteView, CartListView, CartItemDeleteView, AddToCartView, CustomLogoutView, \
    CheckoutListView, \
    AddressCreateView, AddressUpdateView, OrderCreateView, OrderListView, OrderDetailView, OrderDeleteView, \
    OrderPdfCreateView

urlpatterns = [
    # path('rv/', ProductLIstTemplateView.as_view(), name='product_list'),
    path('', ProductListView.as_view(), name='product_list_page'),
    path('product-detail/<int:pk>/', ProductDetailTemplateView.as_view(), name='product_detail'),

    path('settings', SettingsUpdateView.as_view(), name='settings_page'),
    path('register', RegisterCreateView.as_view(), name='register_page'),

    path('login', LoginView.as_view(
        template_name='apps/auth/login.html',
        redirect_authenticated_user=True
    ), name='login_page'),
    path('logout', CustomLogoutView.as_view(template_name='apps/auth/login.html'), name='logout_page'),

    path('shopping-cart', CartListView.as_view(), name='shopping_cart_page'),
    path('remove-cart/<int:pk>/', CartItemDeleteView.as_view(), name='delete_cart_item'),
    path('add-to-cart/<int:pk>/', AddToCartView.as_view(), name='add_cart_page'),

    path('favorite/<int:pk>', FavouriteView.as_view(), name='add_favorite'),

    path('checkout', CheckoutListView.as_view(), name='checkout_page'),

    path('addres-create', AddressCreateView.as_view(), name='create_address'),
    path('address-update/<int:pk>/', AddressUpdateView.as_view(), name='update_address'),

    path('orders', OrderListView.as_view(), name='orders_list'),
    path('order-create/', OrderCreateView.as_view(), name='order_create'),
    path('order/<int:pk>', OrderDetailView.as_view(), name='order'),
    path('order/delete/<int:pk>', OrderDeleteView.as_view(), name='order_delete'),
    path('download-pdf/<int:pk>', OrderPdfCreateView.as_view(), name='download_pdf'),




]
