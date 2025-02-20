from django.urls import path
from . import views

urlpatterns = [
    path("products/", views.products, name="products"),
    path("products/<slug:slug>/", views.ProductDetailView, name="product-detail"),
    path("add_item/",views.add_item, name="add_item"),
    path("product_in_cart/",views.product_in_cart,name='product_in_cart'),
    path("cart/", views.cart, name="cart"),  
    path("update_quantity/", views.update_quantity, name="update_quantity"), 
    path("remove_item/", views.remove_item, name="remove_item"),
    path("create_paypal_payment/", views.create_paypal_payment, name="create_paypal_payment"),
    path("execute_paypal_payment/", views.execute_paypal_payment, name="execute_paypal_payment"),
    path("cancel_paypal_payment/", views.cancel_paypal_payment, name="cancel_paypal_payment"),
    path("order/<int:order_id>/", views.order_details, name="order_details"),
]