"""
ClimaShield – Payment & Treasury Models
Pydantic models for payment transactions and treasury state.
"""

from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime


class PaymentRequest(BaseModel):
    """Request to create a premium payment."""
    policy_id: str = Field(..., description="Policy to pay premium for")
    amount: Optional[float] = Field(None, description="Override premium amount (uses policy default if empty)")


class PaymentVerifyRequest(BaseModel):
    """Request to verify a payment."""
    payment_id: str = Field(..., description="Payment ID to verify")


class ClaimProcessRequest(BaseModel):
    """Request to process a claim payout."""
    policy_id: str = Field(..., description="Policy ID to process claim for")


class Payment(BaseModel):
    """A completed payment record."""
    payment_id: str
    policy_id: str
    amount: float
    currency: str = "USDC"
    status: str = "pending"  # pending, completed, failed
    tx_hash: Optional[str] = None
    protocol: str = "x402"
    network: str = "goat_testnet3"
    created_at: Optional[str] = None
    verified_at: Optional[str] = None


class TreasuryStatus(BaseModel):
    """Current treasury pool status."""
    total_collected: float = 0.0
    total_paid_out: float = 0.0
    available_liquidity: float = 0.0
    reserved_for_claims: float = 0.0
    transaction_count: int = 0
    currency: str = "USDC"
    network: str = "goat_testnet3"
