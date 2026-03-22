def send_confirmation_email(email: str) -> None:
    """Sends an order confirmation email to the customer."""
    print(f"Sending confirmation to {email}")
    print("Subject: Your order has been confirmed!")
    print("Body: Thank you for your purchase.")
