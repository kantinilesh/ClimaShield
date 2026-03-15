"""
ClimaShield Configuration
Loads environment variables from .env file using pydantic-settings.
"""

from pydantic_settings import BaseSettings
from pydantic import Field


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    # --- Weather API ---
    weather_api_key: str = Field(
        default="",
        description="OpenWeatherMap API key for fetching weather data",
    )

    # --- Telegram ---
    telegram_bot_token: str = Field(
        default="",
        description="Telegram Bot token from @BotFather",
    )

    # --- ERC-8004 Agent Identity ---
    erc8004_agent_id: int = Field(
        default=200,
        description="On-chain agent identity ID",
    )
    erc8004_registry: str = Field(
        default="0x556089008Fc0a60cD09390Eca93477ca254A5522",
        description="ERC-8004 registry contract address",
    )

    # --- x402 / GOAT Payments (Phase 3) ---
    goatx402_api_url: str = Field(
        default="https://api.x402.goat.network",
        description="x402 payment protocol API URL",
    )
    goatx402_merchant_id: str = Field(
        default="hireclawnil",
        description="x402 merchant identifier",
    )
    goatx402_api_key: str = Field(
        default="",
        description="x402 API key",
    )
    goatx402_api_secret: str = Field(
        default="",
        description="x402 API secret",
    )
    receive_wallet: str = Field(
        default="0x34817DDAAb4E804510DAd46dAE9D7127535B9100",
        description="Treasury wallet for receiving premiums",
    )
    goat_private_key: str = Field(
        default="",
        description="Private key for signing GOAT Testnet3 transactions",
    )

    # --- GOAT Testnet3 ---
    goat_rpc_url: str = Field(
        default="https://rpc.testnet3.goat.network",
        description="GOAT Testnet3 RPC endpoint",
    )
    goat_chain_id: int = Field(
        default=48816,
        description="GOAT Testnet3 chain ID",
    )

    # --- Application ---
    app_name: str = "ClimaShield"
    app_version: str = "0.3.0"
    debug: bool = False

    model_config = {
        "env_file": ".env",
        "env_file_encoding": "utf-8",
        "case_sensitive": False,
    }


# Singleton settings instance
settings = Settings()
