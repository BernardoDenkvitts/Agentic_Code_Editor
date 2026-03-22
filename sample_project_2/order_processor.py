from notifier import send_confirmation_email


def process_order(order_id: str, customer_email: str, items: list) -> dict:
    """Processes an order and notifies the customer."""

    total = sum(item["price"] * item["qty"] for item in items)

    order = {
        "id": order_id,
        "email": customer_email,
        "items": items,
        "total": total,
        "status": "confirmed",
    }

    send_confirmation_email(customer_email)

    return order
