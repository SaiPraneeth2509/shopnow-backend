# utils/paypal.py
import paypalrestsdk
from django.conf import settings

# Configure PayPal SDK
paypalrestsdk.configure({
    "mode": settings.PAYPAL_MODE,
    "client_id": settings.PAYPAL_CLIENT_ID,
    "client_secret": settings.PAYPAL_CLIENT_SECRET,
})

def create_payment(total, currency, return_url, cancel_url):
    payment = paypalrestsdk.Payment({
        "intent": "sale",
        "payer": {"payment_method": "paypal"},
        "redirect_urls": {
            "return_url": return_url,
            "cancel_url": cancel_url,
        },
        "transactions": [{
            "amount": {
                "total": f"{total:.2f}",
                "currency": currency,
            },
            "description": "Payment for order",
        }],
    })

    if payment.create():
        print("Payment created successfully:", payment)
        return {"success": True, "payment": payment}
    else:
        print("Payment creation failed:", payment.error)
        return {"success": False, "error": payment.error}