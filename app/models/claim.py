"""
ClimaShield – Claim Model
Defines the insurance claim schema.
"""

from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime


class Claim(BaseModel):
    """Represents an insurance claim triggered by parametric conditions."""

    claim_id: str = Field(..., description="Unique claim identifier")
    policy_id: str = Field(..., description="Associated policy ID")
    trigger_event: str = Field(
        ..., description="Description of the trigger event, e.g. rainfall_threshold_exceeded"
    )
    status: str = Field(
        default="pending",
        description="Claim status: pending, approved, rejected, paid",
    )
    payout_amount: Optional[float] = Field(
        default=None, description="Payout amount if claim is approved"
    )
    timestamp: datetime = Field(
        default_factory=datetime.utcnow,
        description="Timestamp when the claim was created",
    )


class TriggerCheckRequest(BaseModel):
    """Request body for checking policy triggers."""

    policy_id: str = Field(..., description="Policy ID to check triggers for")


class TriggerCheckResponse(BaseModel):
    """Response from a trigger check."""

    claim_valid: bool = Field(..., description="Whether the trigger conditions are met")
    trigger_reason: Optional[str] = Field(
        default=None, description="Reason the trigger fired"
    )
    weather_data: Optional[dict] = Field(
        default=None, description="Weather data used for evaluation"
    )
    claim: Optional[Claim] = Field(
        default=None, description="Created claim if trigger is valid"
    )
