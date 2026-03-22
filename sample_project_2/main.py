from order_processor import process_order

if __name__ == "__main__":
    order = process_order(
        order_id="ORD-001",
        customer_email="customer@example.com",
        items=[
            {"name": "Notebook", "price": 3500.00, "qty": 1},
            {"name": "Mouse",    "price":   89.90, "qty": 2},
        ],
    )
    print(f"\nOrder result: {order}")
