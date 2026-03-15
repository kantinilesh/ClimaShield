"""
ClimaShield – Payout Service
Automated orchestration of claim payouts.

Flow:
  1. Claim validated → fraud checks
  2. Treasury reserves funds
  3. GOAT wallet sends transaction
  4. Proof stored to LazAI
  5. Claim status updated
"""

import logging
from datetime import datetime
from typing import Optional

from payments.goat_wallet import send_transaction
from payments.treasury_manager import reserve_for_claim, execute_payout, get_status
from lazai.lazai_client import store_event

logger = logging.getLogger("climashield.payout")


async def process_claim_payout(
    claim_id: str,
    policy_id: str,
    payout_amount: float,
    user_wallet: str,
    trigger_event: str,
    location: str,
    proof_dataset: Optional[str] = None,
) -> dict:
    """
    Execute a full automated claim payout.

    Steps:
      1. Run fraud prevention checks
      2. Reserve funds in treasury
      3. Send GOAT transaction
      4. Store payment proof
      5. Update treasury

    Args:
        claim_id: Verified claim ID.
        policy_id: Associated policy.
        payout_amount: Amount to pay.
        user_wallet: Recipient wallet address.
        trigger_event: What triggered the claim.
        location: City/location.
        proof_dataset: LazAI proof dataset ID (if exists).

    Returns:
        {
            "status": "payout_sent",
            "claim_id": "CLM-...",
            "tx_hash": "0x...",
            "amount": 500,
            "treasury_status": { ... }
        }
    """
    logger.info(f"[PAYOUT] Processing payout for claim {claim_id}: {payout_amount} BTC")

    # Step 1: Fraud prevention checks
    fraud_check = _fraud_prevention_check(
        claim_id=claim_id,
        policy_id=policy_id,
        proof_dataset=proof_dataset,
    )
    if not fraud_check["passed"]:
        return {
            "status": "rejected",
            "claim_id": claim_id,
            "reason": fraud_check["reason"],
            "tx_hash": None,
        }

    # Step 2: Reserve funds in treasury
    reservation = reserve_for_claim(claim_id, payout_amount)
    if not reservation["success"]:
        return {
            "status": "insufficient_funds",
            "claim_id": claim_id,
            "reason": reservation["reason"],
            "tx_hash": None,
            "treasury_status": reservation["treasury"],
        }

    # Step 3: Send GOAT transaction
    tx_result = send_transaction(
        wallet_address=user_wallet or "0x0000000000000000000000000000000000000000",
        amount=payout_amount,
        memo=f"ClimaShield claim payout: {claim_id} ({trigger_event})",
    )

    # Step 4: Store payment proof in LazAI
    payment_proof = store_event(
        event_type="claim_payout",
        value=payout_amount,
        threshold=0,
        location=location,
        weather_data={
            "claim_id": claim_id,
            "policy_id": policy_id,
            "tx_hash": tx_result["tx_hash"],
            "trigger_event": trigger_event,
        },
        validation={"valid": True, "confidence": 1.0, "type": "payment_proof"},
    )

    # Step 5: Update treasury
    treasury_status = execute_payout(
        claim_id=claim_id,
        amount=payout_amount,
        tx_hash=tx_result["tx_hash"],
        wallet=user_wallet or "unspecified",
    )

    result = {
        "status": "payout_sent",
        "claim_id": claim_id,
        "policy_id": policy_id,
        "amount": payout_amount,
        "currency": "BTC",
        "tx_hash": tx_result["tx_hash"],
        "block_number": tx_result["block_number"],
        "explorer_url": tx_result["explorer_url"],
        "payment_proof_id": payment_proof["dataset_id"],
        "treasury_status": treasury_status,
        "network": "goat_testnet3",
        "timestamp": datetime.utcnow().isoformat() + "Z",
    }

    logger.info(
        f"[PAYOUT] Claim {claim_id} paid: {payout_amount} BTC → "
        f"tx={tx_result['tx_hash'][:18]}..."
    )

    return result


def _fraud_prevention_check(
    claim_id: str,
    policy_id: str,
    proof_dataset: Optional[str] = None,
) -> dict:
    """
    Basic fraud prevention checks before payout.

    Validates:
      - Policy ID exists and is valid format
      - Claim ID exists and is valid format
      - Proof dataset exists (if provided)

    Returns:
        {"passed": True/False, "reason": "..."}
    """
    # Check policy ID format
    if not policy_id or not policy_id.startswith("CS"):
        return {"passed": False, "reason": f"Invalid policy ID format: {policy_id}"}

    # Check claim ID format
    if not claim_id or not claim_id.startswith("CLM-"):
        return {"passed": False, "reason": f"Invalid claim ID format: {claim_id}"}

    # Check proof dataset if provided
    if proof_dataset:
        from lazai.lazai_client import verify_proof
        proof = verify_proof(proof_dataset)
        if not proof["verified"]:
            return {"passed": False, "reason": f"Proof dataset unverified: {proof_dataset}"}

    return {"passed": True, "reason": "All fraud checks passed"}
