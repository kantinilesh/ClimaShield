"""
ClimaShield – Identity Service
ERC-8004 Agent Identity management.

Provides on-chain agent identity for the ClimaShield AI agent,
establishing verifiable proof of the agent's existence and capabilities.
"""

from app.config import settings


def get_agent_identity() -> dict:
    """
    Retrieve the ERC-8004 agent identity from configuration.

    Returns:
        {
            "agent_id": 200,
            "registry": "0x556089008Fc0a60cD09390Eca93477ca254A5522",
            "agent_name": "ClimaShield",
            "version": "0.1.0",
            "capabilities": [
                "parametric_insurance",
                "weather_monitoring",
                "risk_assessment",
                "claim_verification"
            ]
        }
    """
    return {
        "agent_id": settings.erc8004_agent_id,
        "registry": settings.erc8004_registry,
        "agent_name": settings.app_name,
        "version": settings.app_version,
        "capabilities": [
            "parametric_insurance",
            "weather_monitoring",
            "risk_assessment",
            "claim_verification",
        ],
    }


def verify_agent_identity() -> bool:
    """
    Verify that agent identity is properly configured.
    In Phase 1, this simply checks that the config values are set.
    Full on-chain verification will be added in Phase 2.
    """
    return (
        settings.erc8004_agent_id > 0
        and len(settings.erc8004_registry) > 0
    )
