from pydantic import BaseModel
from datetime import datetime


class Transaction(BaseModel):
    """Model representing a financial transaction."""

    transaction_id: str
    customer_id: str
    amount: float
    currency: str
    country: str
    channel: str
    device_id: str
    timestamp: datetime
    merchant_id: str
