"""
ClimaShield – Policy Model
Defines the parametric insurance policy schema.
"""

from pydantic import BaseModel, Field
from typing import Optional


class PolicyCreate(BaseModel):
    """Request body for creating a new policy."""

    location: str = Field(..., description="City or region for coverage")
    coverage_type: str = Field(
        ..., description="Type of coverage: rainfall, temperature, aqi"
    )
    user_wallet: Optional[str] = Field(
        default=None, description="User wallet address (optional in Phase 1)"
    )


class Policy(BaseModel):
    """Full policy record stored in the system."""

    policy_id: str = Field(..., description="Unique policy identifier, e.g. CS1001")
    user_wallet: Optional[str] = Field(
        default=None, description="User wallet address"
    )
    location: str = Field(..., description="City or region for coverage")
    coverage_type: str = Field(
        ..., description="Type: rainfall, temperature, aqi"
    )
    trigger_threshold: float = Field(
        ..., description="Value that triggers an automatic payout"
    )
    premium_weekly: float = Field(..., description="Weekly premium in INR")
    coverage_amount: float = Field(..., description="Payout amount in INR")
    status: str = Field(default="active", description="Policy status")


# Default trigger thresholds per coverage type
DEFAULT_THRESHOLDS = {
    "rainfall": 40.0,      # mm
    "temperature": 42.0,   # °C
    "aqi": 250.0,          # AQI index
    "flood_alert": 1.0,    # alert flag
}

# Default premiums per coverage type (low for testnet testing)
DEFAULT_PREMIUMS = {
    "rainfall": 2.0,       # USDC
    "temperature": 3.0,    # USDC
    "aqi": 2.0,            # USDC
    "flood_alert": 5.0,    # USDC
}

# Default coverage amounts (low for testnet testing)
DEFAULT_COVERAGE = {
    "rainfall": 10.0,      # USDC
    "temperature": 15.0,   # USDC
    "aqi": 10.0,           # USDC
    "flood_alert": 12.0,   # USDC
}

