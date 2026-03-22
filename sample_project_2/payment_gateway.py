def process_payment(amount: float, card_number: str) -> bool:
    """Mock process payment."""
    print(f"Processing payment of {amount} with card {card_number[-4:]}")
    if amount <= 0:
        return False
    return True
