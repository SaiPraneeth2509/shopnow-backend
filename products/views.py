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

        # Get or create the cart
        cart, created = Cart.objects.get_or_create(cart_code=cart_code)

        # Set the user if the user is authenticated
        if request.user.is_authenticated:
            cart.user = request.user
            cart.save()

        # Add the product to the cart
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
        return Response({"total_items": 0, "items": []}, status=status.HTTP_200_OK)


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
    


from django.conf import settings
from django.urls import reverse
from django.shortcuts import redirect
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from .models import Cart
from core.models import Order,OrderItem
from .serializers import CartSerializer
from core.serializers import OrderSerializer
from products.utils.paypal import create_payment 
import paypalrestsdk  

@api_view(["POST"])
def create_paypal_payment(request):
    cart_code = request.data.get("cart_code")
    if not cart_code:
        return Response(
            {"error": "cart_code is required"},
            status=status.HTTP_400_BAD_REQUEST,
        )

    try:
        cart = Cart.objects.get(cart_code=cart_code)
    except Cart.DoesNotExist:
        return Response(
            {"error": "Cart not found"},
            status=status.HTTP_404_NOT_FOUND,
        )

    # Calculate total price
    cart_items = cart.items.all()
    total_price = sum(item.product.price * item.quantity for item in cart_items)

    # Create PayPal payment
    return_url = request.build_absolute_uri(reverse("execute_paypal_payment"))
    cancel_url = request.build_absolute_uri(reverse("cancel_paypal_payment"))
    payment_response = create_payment(total_price, "USD", return_url, cancel_url)

    if not payment_response["success"]:
        return Response(
            {"error": payment_response["error"]},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )

    # Save payment ID to the cart
    cart.paypal_payment_id = payment_response["payment"].id  # Save PayPal payment ID
    cart.save()

    # Return PayPal approval URL
    for link in payment_response["payment"].links:
        if link.method == "REDIRECT":
            return Response({"approval_url": link.href}, status=status.HTTP_200_OK)

    return Response(
        {"error": "No approval URL found"},
        status=status.HTTP_500_INTERNAL_SERVER_ERROR,
    )



@api_view(["GET"])
def execute_paypal_payment(request):
    payment_id = request.query_params.get("paymentId")
    payer_id = request.query_params.get("PayerID")

    if not payment_id or not payer_id:
        return Response(
            {"error": "paymentId and PayerID are required"},
            status=status.HTTP_400_BAD_REQUEST,
        )

    try:
        cart = Cart.objects.get(paypal_payment_id=payment_id)
    except Cart.DoesNotExist:
        return Response(
            {"error": "Cart not found"},
            status=status.HTTP_404_NOT_FOUND,
        )

    # Ensure the cart has a user
    if not cart.user:
        return Response(
            {"error": "Cart is not associated with a user"},
            status=status.HTTP_400_BAD_REQUEST,
        )

    # Execute payment
    payment = paypalrestsdk.Payment.find(payment_id)
    if payment.execute({"payer_id": payer_id}):
        # Mark cart as paid
        cart.paid = True
        cart.save()

        # Create an order
        order = Order.objects.create(
            user=cart.user,
            total_price=sum(item.product.price * item.quantity for item in cart.items.all()),
        )

        # Create OrderItem entries for each product in the cart
        for cart_item in cart.items.all():
            OrderItem.objects.create(
                order=order,
                product=cart_item.product,
                quantity=cart_item.quantity,
            )
        
        # Redirect to the frontend Payment Success page
        frontend_success_url = f"{settings.FRONTEND_URL}/payment-success?order_id={order.id}"
        return redirect(frontend_success_url)
    else:
        return Response(
            {"error": payment.error},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )
        


@api_view(["GET"])
def cancel_paypal_payment(request):
    return Response(
        {"message": "Payment canceled"},
        status=status.HTTP_200_OK,
    )

@api_view(["GET"])
def order_details(request, order_id):
    try:
        # Fetch the order with related items and products
        order = Order.objects.prefetch_related('items__product').get(id=order_id)
        serializer = OrderSerializer(order)
        return Response(serializer.data, status=status.HTTP_200_OK)
    except Order.DoesNotExist:
        return Response(
            {"error": "Order not found"},
            status=status.HTTP_404_NOT_FOUND,
        )
    except Exception as e:
        # Log the error for debugging
        print(f"Error fetching order details: {e}")
        return Response(
            {"error": "An error occurred while fetching order details."},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )