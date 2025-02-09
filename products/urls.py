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
]