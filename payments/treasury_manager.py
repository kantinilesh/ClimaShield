"""
ClimaShield – Treasury Manager
Manages the premium pool used to fund claim payouts.

Tracks:
  - Total premiums collected
  - Available liquidity
  - Reserved for pending claims
  - Payment history
"""

import json
import logging
from datetime import datetime
from pathlib import Path
from typing import Optional

logger = logging.getLogger("climashield.treasury")

TREASURY_FILE = Path(__file__).parent.parent / "data" / "treasury.json"


def _load_treasury() -> dict:
    """Load treasury state from disk."""
    if not TREASURY_FILE.exists():
        return {
            "total_collected": 0.0,
            "total_paid_out": 0.0,
            "available_liquidity": 0.0,
            "reserved_for_claims": 0.0,
            "transactions": [],
        }
    with open(TREASURY_FILE, "r") as f:
        return json.load(f)


def _save_treasury(treasury: dict) -> None:
    """Persist treasury state."""
    TREASURY_FILE.parent.mkdir(parents=True, exist_ok=True)
    with open(TREASURY_FILE, "w") as f:
        json.dump(treasury, f, indent=2, default=str)


def deposit_premium(
    payment_id: str,
    policy_id: str,
    amount: float,
    tx_hash: str = "",
) -> dict:
    """
    Record a premium deposit into the treasury pool.

    Args:
        payment_id: x402 payment ID.
        policy_id: Associated policy.
        amount: Premium amount.
        tx_hash: On-chain transaction hash.

    Returns:
        Updated treasury status.
    """
    treasury = _load_treasury()

    transaction = {
        "type": "premium_deposit",
        "payment_id": payment_id,
        "policy_id": policy_id,
        "amount": amount,
        "tx_hash": tx_hash,
        "timestamp": datetime.utcnow().isoformat() + "Z",
    }

    treasury["total_collected"] += amount
    treasury["available_liquidity"] += amount
    treasury["transactions"].append(transaction)

    _save_treasury(treasury)

    logger.info(
        f"[TREASURY] Deposit: +{amount} USDC from {policy_id} "
        f"(total: {treasury['total_collected']})"
    )

    return get_status()


def reserve_for_claim(claim_id: str, amount: float) -> dict:
    """
    Reserve funds from liquidity for a pending claim payout.

    Returns:
        {"success": True/False, "reason": "...", "treasury": {...}}
    """
    treasury = _load_treasury()

    if treasury["available_liquidity"] < amount:
        return {
            "success": False,
            "reason": f"Insufficient liquidity: {treasury['available_liquidity']} < {amount}",
            "treasury": get_status(),
        }

    treasury["available_liquidity"] -= amount
    treasury["reserved_for_claims"] += amount
    treasury["transactions"].append({
        "type": "claim_reserve",
        "claim_id": claim_id,
        "amount": amount,
        "timestamp": datetime.utcnow().isoformat() + "Z",
    })

    _save_treasury(treasury)

    logger.info(f"[TREASURY] Reserved {amount} USDC for claim {claim_id}")
    return {"success": True, "reason": "Funds reserved", "treasury": get_status()}


def execute_payout(
    claim_id: str,
    amount: float,
    tx_hash: str,
    wallet: str,
) -> dict:
    """
    Record a completed payout from reserved funds.

    Args:
        claim_id: Claim that was paid.
        amount: Payout amount.
        tx_hash: GOAT transaction hash.
        wallet: Recipient wallet.

    Returns:
        Updated treasury status.
    """
    treasury = _load_treasury()

    treasury["reserved_for_claims"] = max(0, treasury["reserved_for_claims"] - amount)
    treasury["total_paid_out"] += amount
    treasury["transactions"].append({
        "type": "claim_payout",
        "claim_id": claim_id,
        "amount": amount,
        "tx_hash": tx_hash,
        "wallet": wallet,
        "timestamp": datetime.utcnow().isoformat() + "Z",
    })

    _save_treasury(treasury)

    logger.info(
        f"[TREASURY] Payout: -{amount} USDC for {claim_id} → {wallet[:12]}... "
        f"(remaining: {treasury['available_liquidity']})"
    )

    return get_status()


def get_status() -> dict:
    """
    Get current treasury status.

    Returns:
        {
            "total_collected": 10000,
            "total_paid_out": 3000,
            "available_liquidity": 7000,
            "reserved_for_claims": 0,
            "transaction_count": 15
        }
    """
    treasury = _load_treasury()
    return {
        "total_collected": treasury["total_collected"],
        "total_paid_out": treasury["total_paid_out"],
        "available_liquidity": treasury["available_liquidity"],
        "reserved_for_claims": treasury["reserved_for_claims"],
        "transaction_count": len(treasury["transactions"]),
        "currency": "USDC",
        "network": "goat_testnet3",
    }
