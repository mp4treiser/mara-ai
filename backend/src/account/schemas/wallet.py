from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field


class WalletBase(BaseModel):
    network: str = Field(default="APTOS", description="Сеть кошелька")


class WalletCreate(WalletBase):
    pass


class WalletResponse(WalletBase):
    id: int
    user_id: int
    address: str
    network: str
    is_active: bool
    created_at: datetime
    last_checked: Optional[datetime] = None
    
    class Config:
        from_attributes = True


class WalletDepositResponse(BaseModel):
    id: int
    wallet_id: int
    transaction_hash: str
    amount: float
    usd_amount: float
    status: str
    block_number: Optional[int] = None
    created_at: datetime
    processed_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True


class WalletBalanceResponse(BaseModel):
    wallet_address: str
    network: str
    usdt_balance: float
    usd_equivalent: float
    last_updated: datetime
