from payment_gateway import process_payment

def finalize_order(cart_total: float, user_card: str) -> str:
    print(f"Finalizing order for total: {cart_total}")

    success = process_payment(cart_total, user_card)
    
    if success:
        return "Order confirmed!"
    else:
        return "Payment failed."
