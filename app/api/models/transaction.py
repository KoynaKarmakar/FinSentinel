from pydantic import BaseModel, Field


class TransactionInput(BaseModel):
    account_id: str = Field(..., description="Unique account identifier")
    amount_inr: float = Field(..., gt=0, description="Transaction amount in Indian Rupees")
    velocity_24h: int = Field(..., ge=0, description="Number of transactions in the last 24 hours")
    account_age_days: int = Field(..., ge=0, description="Age of the account in days")
    is_cross_border: bool = Field(..., description="Whether the transaction crosses a national border")
