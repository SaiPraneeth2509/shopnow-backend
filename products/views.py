from django.shortcuts import render
from rest_framework.decorators import api_view
from rest_framework import status
from .models import Product,Cart,CartItem
from .serializers import ProductSerializer,CartItemSerializer,CartSerializer
from rest_framework.response import Response

# Create your views here.
@api_view(["GET"])
def products(request):
    products = Product.objects.all()
    serializer = ProductSerializer(products,many=True)
    return Response(serializer.data)

@api_view(["GET"])
def ProductDetailView(request,slug):
    try:
        product = Product.objects.get(slug=slug)
        serializer = ProductSerializer(product)
        return Response(serializer.data)
    except Product.DoesNotExist:
        return Response(
            {"error": "Product not found"},
            status=status.HTTP_404_NOT_FOUND)
    

@api_view(["POST"])
def add_item(request):
    try:
        cart_code = request.data.get("cart_code")
        product_id = request.data.get("product_id")

        if not cart_code or not product_id:
            return Response(
                {"error": "cart_code and product_id are required"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        cart, created = Cart.objects.get_or_create(cart_code=cart_code)

        try:
            product = Product.objects.get(id=product_id)
        except Product.DoesNotExist:
            return Response(
                {"error": "Product not found"},
                status=status.HTTP_404_NOT_FOUND,
            )

        cart_item, created = CartItem.objects.get_or_create(cart=cart, product=product)

        if not created:
            cart_item.quantity += 1  
        else:
            cart_item.quantity = 1  

        cart_item.save()

        serializer = CartItemSerializer(cart_item)
        return Response(
            {"data": serializer.data, "message": "Item added to cart successfully"},
            status=status.HTTP_201_CREATED,
        )

    except Exception as e:
        return Response(
            {"error": str(e)},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )

@api_view(["GET"])
def product_in_cart(request):
    try:
        cart_code = request.query_params.get("cart_code")
        product_id = request.query_params.get("product_id")

        if not cart_code or not product_id:
            return Response(
                {"error": "cart_code and product_id are required"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            cart = Cart.objects.get(cart_code=cart_code)
        except Cart.DoesNotExist:
            return Response(
                {"error": "Cart not found"},
                status=status.HTTP_404_NOT_FOUND,
            )

        try:
            product = Product.objects.get(id=product_id)
        except Product.DoesNotExist:
            return Response(
                {"error": "Product not found"},
                status=status.HTTP_404_NOT_FOUND,
            )

        product_exists_in_cart = CartItem.objects.filter(cart=cart, product=product).exists()

        return Response({"product_in_cart": product_exists_in_cart}, status=status.HTTP_200_OK)

    except Exception as e:
        return Response(
            {"error": str(e)},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )
    

@api_view(["GET"])
def cart(request):
    cart_code = request.GET.get("cart_code")
    if not cart_code:
        return Response(
            {"error": "cart_code is required"},
            status=status.HTTP_400_BAD_REQUEST,
        )

    try:
        cart = Cart.objects.get(cart_code=cart_code)
        cart_items = CartItem.objects.filter(cart=cart)
        serializer = CartItemSerializer(cart_items, many=True)
        return Response({
            "items": serializer.data,
            "total_items": cart_items.count(),
        }, status=status.HTTP_200_OK)
    except Cart.DoesNotExist:
        return Response(
            {"error": "Cart not found"},
            status=status.HTTP_404_NOT_FOUND,
        )


@api_view(["POST"])
def update_quantity(request):
    cart_code = request.data.get("cart_code")
    product_id = request.data.get("product_id")
    quantity = request.data.get("quantity")

    if not cart_code or not product_id or not quantity:
        return Response(
            {"error": "cart_code, product_id, and quantity are required"},
            status=status.HTTP_400_BAD_REQUEST,
        )

    try:
        cart = Cart.objects.get(cart_code=cart_code)
        cart_item = CartItem.objects.get(cart=cart, product_id=product_id)
        cart_item.quantity = quantity
        cart_item.save()
        serializer = CartItemSerializer(cart_item)
        return Response({
            "message": "Quantity updated successfully",
            "data": serializer.data,
        }, status=status.HTTP_200_OK)
    except Cart.DoesNotExist:
        return Response(
            {"error": "Cart not found"},
            status=status.HTTP_404_NOT_FOUND,
        )
    except CartItem.DoesNotExist:
        return Response(
            {"error": "Product not found in cart"},
            status=status.HTTP_404_NOT_FOUND,
        )
    


@api_view(["POST"])
def remove_item(request):
    cart_code = request.data.get("cart_code")
    product_id = request.data.get("product_id")

    if not cart_code or not product_id:
        return Response(
            {"error": "cart_code and product_id are required"},
            status=status.HTTP_400_BAD_REQUEST,
        )

    try:
        cart = Cart.objects.get(cart_code=cart_code)
        cart_item = CartItem.objects.get(cart=cart, product_id=product_id)
        cart_item.delete()
        return Response(
            {"message": "Item removed from cart successfully"},
            status=status.HTTP_200_OK,
        )
    except Cart.DoesNotExist:
        return Response(
            {"error": "Cart not found"},
            status=status.HTTP_404_NOT_FOUND,
        )
    except CartItem.DoesNotExist:
        return Response(
            {"error": "Product not found in cart"},
            status=status.HTTP_404_NOT_FOUND,
        )