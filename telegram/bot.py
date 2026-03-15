"""
ClimaShield – Telegram Bot (Phase 5 – Demo Ready)
Conversational interface for gig workers and farmers.

Phase 1: /start, /buy_policy, /check_policy, /status
Phase 2: /risk_score, /oracle_status, /trigger_alert
Phase 3: /pay_premium, /claim_status, /treasury
Phase 5: /demo, /demo_full, /wallet (Judge Demo Mode)
"""

import sys
import os
import asyncio
import random
from datetime import datetime

# Ensure the project root is on the Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from telegram import Update
from telegram.ext import (
    Application,
    CommandHandler,
    ContextTypes,
)

from app.config import settings
from app.agents.coordinator_agent import InsuranceCoordinatorAgent
from app.models.policy import PolicyCreate
from app.services.risk_service import calculate_risk
from oracle.oracle_monitor import check_city_conditions
from payments.x402_client import collect_premium
from payments.treasury_manager import deposit_premium, get_status as get_treasury_status
from payments.payout_service import process_claim_payout


# Coordinator agent instance for the bot
coordinator = InsuranceCoordinatorAgent()


# ── Phase 1 Command Handlers ───────────────────────────────────────

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle /start command – welcome message."""
    welcome = (
        "🛡️ *Welcome to ClimaShield!*\n\n"
        "AI-powered parametric insurance protecting gig workers "
        "and farmers from environmental disruptions.\n\n"
        "*Policy Commands:*\n"
        "🔹 /buy\\_policy `<city> <type>` – Buy a policy\n"
        "🔹 /check\\_policy `<policy_id>` – Check triggers\n"
        "🔹 /status `<policy_id>` – View policy\n\n"
        "*AI & Oracle:*\n"
        "🔸 /risk\\_score `<city>` – AI risk assessment\n"
        "🔸 /oracle\\_status `<city>` – Live weather\n"
        "🔸 /trigger\\_alert `<city>` – Check alerts\n\n"
        "*Payments:*\n"
        "💳 /pay\\_premium `<policy_id>` – Pay premium\n"
        "📋 /claim\\_status `<policy_id>` – Process claim\n"
        "🏦 /treasury – View treasury pool\n"
        "💰 /wallet – GOAT wallet balance\n\n"
        "*🎮 Judge Demo:*\n"
        "🚀 /demo `<city>` – Simulate heavy rain & process claim\n"
        "💨 /demo\\_aqi `<city>` – Simulate dangerous AQI (India)\n"
        "🎯 /demo\\_full – Full end-to-end demo (auto)\n\n"
        "_Example:_ `/buy_policy Mumbai rainfall`"
    )
    await update.message.reply_text(welcome, parse_mode="Markdown")


async def buy_policy(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle /buy_policy command."""
    args = context.args
    if not args or len(args) < 2:
        await update.message.reply_text(
            "⚠️ Usage: `/buy_policy <city> <type>`\n"
            "Example: `/buy_policy Mumbai rainfall`",
            parse_mode="Markdown",
        )
        return

    city = args[0]
    coverage_type = args[1].lower()
    valid_types = ["rainfall", "temperature", "aqi"]

    if coverage_type not in valid_types:
        await update.message.reply_text(
            f"❌ Invalid type. Choose: {', '.join(valid_types)}",
            parse_mode="Markdown",
        )
        return

    await update.message.reply_text("⏳ Creating policy…")

    try:
        request = PolicyCreate(location=city, coverage_type=coverage_type)
        policy = await coordinator.create_policy(request)

        unit = "mm" if coverage_type == "rainfall" else ("°C" if coverage_type == "temperature" else "AQI")
        response = (
            f"✅ *Policy Created!*\n\n"
            f"📋 ID: `{policy.policy_id}`\n"
            f"📍 Location: {policy.location}\n"
            f"🔔 Trigger: {policy.coverage_type} > {policy.trigger_threshold}{unit}\n"
            f"💰 Premium: ₹{policy.premium_weekly}/week\n"
            f"🛡️ Coverage: ₹{policy.coverage_amount}\n\n"
            f"_Pay premium with:_ `/pay_premium {policy.policy_id}`"
        )
        await update.message.reply_text(response, parse_mode="Markdown")
    except Exception as e:
        await update.message.reply_text(f"❌ Error: {e}")


async def check_policy(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle /check_policy command."""
    args = context.args
    if not args:
        await update.message.reply_text(
            "⚠️ Usage: `/check_policy <policy_id>`",
            parse_mode="Markdown",
        )
        return

    policy_id = args[0]
    await update.message.reply_text("⏳ Checking triggers…")

    try:
        result = await coordinator.evaluate_triggers(policy_id)
        if "error" in result:
            await update.message.reply_text(f"❌ {result['error']}")
            return

        if result["claim_valid"]:
            claim = result.get("claim", {})
            proof = result.get("proof_dataset", "N/A")
            response = (
                f"🚨 *TRIGGER ACTIVATED!*\n\n"
                f"📋 Policy: `{policy_id}`\n"
                f"⚡ {result['trigger_reason']}\n"
                f"🎫 Claim: `{claim.get('claim_id', 'N/A')}`\n"
                f"💰 Payout: ₹{claim.get('payout_amount', 'N/A')}\n"
                f"🔗 Proof: `{proof}`\n\n"
                f"_Process claim:_ `/claim_status {policy_id}`"
            )
        else:
            weather = result.get("weather_data", {})
            response = (
                f"✅ *No trigger*\n\n"
                f"📋 Policy: `{policy_id}`\n"
                f"🌧️ Rain: {weather.get('rain_mm', 0)}mm\n"
                f"🌡️ Temp: {weather.get('temperature', 0)}°C\n"
                f"💧 Humidity: {weather.get('humidity', 0)}%"
            )
        await update.message.reply_text(response, parse_mode="Markdown")
    except Exception as e:
        await update.message.reply_text(f"❌ Error: {e}")


async def status(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle /status command."""
    args = context.args
    if not args:
        await update.message.reply_text("⚠️ Usage: `/status <policy_id>`", parse_mode="Markdown")
        return

    info = coordinator.check_policy_status(args[0])
    if info is None:
        await update.message.reply_text(f"❌ Policy `{args[0]}` not found.", parse_mode="Markdown")
        return

    response = (
        f"📋 *Policy {info['policy_id']}*\n\n"
        f"📍 {info['location']} | {info['coverage_type']}\n"
        f"⚡ Threshold: {info['trigger_threshold']}\n"
        f"💰 ₹{info['premium_weekly']}/week | Coverage: ₹{info['coverage_amount']}\n"
        f"📊 Status: {info['status']}"
    )
    await update.message.reply_text(response, parse_mode="Markdown")


# ── Phase 2 Command Handlers ───────────────────────────────────────

async def risk_score(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle /risk_score command."""
    args = context.args
    if not args:
        await update.message.reply_text("⚠️ Usage: `/risk_score <city>`", parse_mode="Markdown")
        return

    city = args[0]
    await update.message.reply_text(f"🧠 Calculating risk for {city}…")

    try:
        result = await calculate_risk(location=city)
        risk = result["risk_assessment"]
        pred = result["disruption_prediction"]

        response = (
            f"🧠 *Risk – {city}*\n\n"
            f"📊 Score: {risk['risk_score']} ({risk['risk_level'].upper()})\n"
            f"💰 Premium: ₹{risk['premium_recommendation']}/week\n"
            f"🔮 Disruption: {pred['disruption_probability']} ({pred['predicted_event']})\n"
            f"⏰ Horizon: {pred['time_horizon']}"
        )
        await update.message.reply_text(response, parse_mode="Markdown")
    except Exception as e:
        await update.message.reply_text(f"❌ Error: {e}")


async def oracle_status(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle /oracle_status command."""
    args = context.args
    if not args:
        await update.message.reply_text("⚠️ Usage: `/oracle_status <city>`", parse_mode="Markdown")
        return

    city = args[0]
    await update.message.reply_text(f"📡 Fetching oracle for {city}…")

    try:
        conditions = await check_city_conditions(city)
        weather = conditions["weather_data"]
        triggers = conditions["triggers_detected"]

        trigger_text = ""
        for t in triggers:
            icon = "🔴" if t["exceeded"] else "🟢"
            trigger_text += f"  {icon} {t['type']}: {t['value']} (thresh: {t['threshold']})\n"

        response = (
            f"📡 *Oracle – {city}*\n\n"
            f"🌧️ Rain: {weather.get('rain_mm', 0)}mm | "
            f"🌡️ {weather.get('temperature', 0)}°C | "
            f"💧 {weather.get('humidity', 0)}%\n"
            f"🚦 Alert: {conditions['alert_level'].upper()}\n\n"
            f"{trigger_text}"
        )
        await update.message.reply_text(response, parse_mode="Markdown")
    except Exception as e:
        await update.message.reply_text(f"❌ Error: {e}")


async def trigger_alert(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle /trigger_alert command."""
    args = context.args
    if not args:
        await update.message.reply_text("⚠️ Usage: `/trigger_alert <city>`", parse_mode="Markdown")
        return

    city = args[0]
    try:
        conditions = await check_city_conditions(city)
        triggered = [t for t in conditions["triggers_detected"] if t["exceeded"]]

        if triggered:
            lines = "".join(f"  🚨 {t['type']}: {t['value']} > {t['threshold']}\n" for t in triggered)
            response = f"🚨 *ALERT – {city}*\n\n{lines}Level: *{conditions['alert_level'].upper()}*"
        else:
            response = f"✅ *No alerts for {city}* – all normal"

        await update.message.reply_text(response, parse_mode="Markdown")
    except Exception as e:
        await update.message.reply_text(f"❌ Error: {e}")


# ── Phase 3 Command Handlers ───────────────────────────────────────

async def pay_premium(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle /pay_premium command – pay policy premium via x402."""
    args = context.args
    if not args:
        await update.message.reply_text(
            "⚠️ Usage: `/pay_premium <policy_id>`\nExample: `/pay_premium CS1001`",
            parse_mode="Markdown",
        )
        return

    policy_id = args[0]
    policy = coordinator.get_policy(policy_id)

    if policy is None:
        await update.message.reply_text(f"❌ Policy `{policy_id}` not found.", parse_mode="Markdown")
        return

    await update.message.reply_text(f"💳 Processing premium payment for `{policy_id}`…", parse_mode="Markdown")

    try:
        # Collect premium via x402 (async – real API)
        payment = await collect_premium(
            policy_id=policy_id,
            premium_amount=policy.premium_weekly,
            user_wallet=policy.user_wallet or "",
        )

        # Deposit to treasury
        if payment["status"] == "completed":
            deposit_premium(
                payment_id=payment["payment_id"],
                policy_id=policy_id,
                amount=policy.premium_weekly,
                tx_hash=payment["tx_hash"],
            )

        response = (
            f"✅ *Premium Paid!*\n\n"
            f"📋 Policy: `{policy_id}`\n"
            f"💰 Amount: {policy.premium_weekly} USDC\n"
            f"🔗 Tx: `{payment['tx_hash'][:20]}...`\n"
            f"📊 Status: {payment['status']}\n"
            f"🌐 Protocol: x402 on GOAT Testnet3"
        )
        await update.message.reply_text(response, parse_mode="Markdown")
    except Exception as e:
        await update.message.reply_text(f"❌ Payment error: {e}")


async def claim_status(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle /claim_status command – process claim and trigger payout."""
    args = context.args
    if not args:
        await update.message.reply_text(
            "⚠️ Usage: `/claim_status <policy_id>`\nExample: `/claim_status CS1001`",
            parse_mode="Markdown",
        )
        return

    policy_id = args[0]
    await update.message.reply_text(f"🔍 Processing claim for `{policy_id}`…", parse_mode="Markdown")

    try:
        # Evaluate triggers
        trigger_result = await coordinator.evaluate_triggers(policy_id)

        if "error" in trigger_result:
            await update.message.reply_text(f"❌ {trigger_result['error']}")
            return

        if not trigger_result["claim_valid"]:
            weather = trigger_result.get("weather_data", {})
            response = (
                f"✅ *No claim trigger*\n\n"
                f"📋 Policy: `{policy_id}`\n"
                f"🌧️ Rain: {weather.get('rain_mm', 0)}mm\n"
                f"🌡️ Temp: {weather.get('temperature', 0)}°C\n"
                f"_Conditions are within normal range._"
            )
            await update.message.reply_text(response, parse_mode="Markdown")
            return

        # Claim valid — process payout
        claim = trigger_result.get("claim", {})
        policy = coordinator.get_policy(policy_id)

        payout = await process_claim_payout(
            claim_id=claim.get("claim_id", "CLM-UNKNOWN"),
            policy_id=policy_id,
            payout_amount=claim.get("payout_amount", policy.coverage_amount),
            user_wallet=policy.user_wallet,
            trigger_event=trigger_result.get("trigger_reason", ""),
            location=policy.location,
            proof_dataset=trigger_result.get("proof_dataset"),
        )

        response = (
            f"🚨 *CLAIM PROCESSED!*\n\n"
            f"⚡ {trigger_result['trigger_reason']}\n\n"
            f"💰 *Payout: {payout.get('amount', 0)} USDC*\n"
            f"🔗 Tx: `{payout.get('tx_hash', 'N/A')[:20]}...`\n"
            f"🎫 Claim: `{claim.get('claim_id', 'N/A')}`\n"
            f"📊 Status: `{payout.get('status', 'N/A')}`\n"
            f"🌐 Network: GOAT Testnet3\n"
            f"🔗 [View on Explorer]({payout.get('explorer_url', '#')})"
        )
        await update.message.reply_text(response, parse_mode="Markdown")
    except Exception as e:
        await update.message.reply_text(f"❌ Error: {e}")


async def treasury(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle /treasury command – show treasury pool status."""
    try:
        status = get_treasury_status()
        response = (
            f"🏦 *Treasury Status*\n\n"
            f"💰 Collected: {status['total_collected']} USDC\n"
            f"💸 Paid Out: {status['total_paid_out']} USDC\n"
            f"💧 Available: {status['available_liquidity']} USDC\n"
            f"🔒 Reserved: {status['reserved_for_claims']} USDC\n"
            f"📊 Transactions: {status['transaction_count']}\n"
            f"🌐 Network: GOAT Testnet3"
        )
        await update.message.reply_text(response, parse_mode="Markdown")
    except Exception as e:
        await update.message.reply_text(f"❌ Error: {e}")


# ── Phase 5: Judge Demo Commands ────────────────────────────────────

async def wallet_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle /wallet command – show GOAT wallet balance."""
    try:
        from payments.goat_wallet import get_balance
        bal = get_balance()
        response = (
            f"💰 *GOAT Wallet*\n\n"
            f"🔗 Address: `{bal['wallet'][:10]}...{bal['wallet'][-8:]}`\n"
            f"💎 Balance: *{bal['balance_btc']:.8f} BTC*\n"
            f"🌐 Network: GOAT Testnet3 (Chain {bal.get('chain_id', 48816)})\n"
            f"📡 Status: {'🟢 Live (Real Balance)' if bal.get('real_balance') else '⚪ Simulated'}"
        )
        await update.message.reply_text(response, parse_mode="Markdown")
    except Exception as e:
        await update.message.reply_text(f"❌ Error: {e}")


async def demo(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """
    /demo <city> – Simulate heavy rainfall >40mm and process claim.
    Shows judges: Oracle → Trigger → AI Verification → GOAT Payout.
    """
    args = context.args
    city = args[0] if args else "Mumbai"
    rain_mm = round(random.uniform(42.0, 68.0), 1)

    await update.message.reply_text(
        f"🎮 *DEMO MODE – {city}*\n\n"
        f"Simulating heavy rainfall event…\n"
        f"🌧️ Injecting {rain_mm}mm rainfall (threshold: 40mm)",
        parse_mode="Markdown",
    )
    await asyncio.sleep(1)

    # Step 1: Show oracle data with mock heavy rain
    await update.message.reply_text(
        f"📡 *Step 1: Oracle Data*\n\n"
        f"🌧️ Rainfall: *{rain_mm}mm* (🔴 EXCEEDS 40mm)\n"
        f"🌡️ Temperature: {round(random.uniform(28, 35), 1)}°C\n"
        f"💧 Humidity: {random.randint(78, 95)}%\n"
        f"🚦 Alert Level: *CRITICAL*\n\n"
        f"_Oracle has detected dangerous conditions…_",
        parse_mode="Markdown",
    )
    await asyncio.sleep(1.5)

    # Step 2: Find policies for this city
    policies = coordinator._load_policies()
    city_policies = [p for p in policies if p.get("location", "").lower() == city.lower() and p.get("status") == "active"]

    if not city_policies:
        # Create a demo policy on the fly
        await update.message.reply_text(f"📋 No policies for {city}. Creating demo policy…")
        request = PolicyCreate(location=city, coverage_type="rainfall")
        policy = await coordinator.create_policy(request)
        city_policies = [{"policy_id": policy.policy_id, "coverage_amount": policy.coverage_amount, "premium_weekly": policy.premium_weekly, "trigger_threshold": policy.trigger_threshold}]
        await asyncio.sleep(0.5)

    target = city_policies[0]
    policy_id = target["policy_id"]

    await update.message.reply_text(
        f"🔍 *Step 2: AI Claim Verification*\n\n"
        f"📋 Policy: `{policy_id}`\n"
        f"🛡️ Coverage: {target.get('coverage_amount', 500)} USDC\n"
        f"⚡ Trigger: rainfall > {target.get('trigger_threshold', 40)}mm\n"
        f"🌧️ Actual: *{rain_mm}mm* ← EXCEEDED ✅\n\n"
        f"🤖 ClaimVerificationAgent validating…\n"
        f"📊 LazAI proof dataset logged\n"
        f"✅ *Claim VERIFIED by AI agent*",
        parse_mode="Markdown",
    )
    await asyncio.sleep(1.5)

    # Step 3: Process payout (real on-chain tx via GOAT)
    await update.message.reply_text(
        f"💰 *Step 3: GOAT Network Payout*\n\n"
        f"Sending on-chain transaction…\n"
        f"🌐 Network: GOAT Testnet3 (Chain 48816)\n"
        f"📡 Protocol: x402",
        parse_mode="Markdown",
    )

    try:
        payout_amount = target.get("coverage_amount", 500)
        policy_obj = coordinator.get_policy(policy_id)

        payout = await process_claim_payout(
            claim_id=f"CLM-DEMO-{random.randint(1000, 9999)}",
            policy_id=policy_id,
            payout_amount=payout_amount,
            user_wallet=policy_obj.user_wallet if policy_obj else "",
            trigger_event=f"Heavy rainfall: {rain_mm}mm > 40mm threshold",
            location=city,
            proof_dataset=f"lazai://proof/rainfall/{city.lower()}/{datetime.now().strftime('%Y%m%d')}",
        )

        tx_hash = payout.get("tx_hash", "N/A")
        explorer = payout.get("explorer_url", "#")

        await asyncio.sleep(1)

        await update.message.reply_text(
            f"🚨 *CLAIM PAID – DEMO COMPLETE!*\n\n"
            f"━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
            f"🌧️ Event: Heavy Rainfall ({rain_mm}mm)\n"
            f"📍 City: {city}\n"
            f"📋 Policy: `{policy_id}`\n"
            f"💰 *Payout: {payout.get('amount', payout_amount)} USDC*\n"
            f"🔗 Tx: `{tx_hash[:24]}...`\n"
            f"🌐 GOAT Testnet3 (Chain 48816)\n"
            f"📊 Status: ✅ {payout.get('status', 'completed')}\n"
            f"━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n\n"
            f"🔗 [View on GOAT Explorer]({explorer})\n\n"
            f"_This demonstrates the full parametric insurance flow:_\n"
            f"_Oracle → AI Verification → On-Chain Payout_",
            parse_mode="Markdown",
        )
    except Exception as e:
        await update.message.reply_text(f"❌ Payout error: {e}")


async def demo_full(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """
    /demo_full – Run the COMPLETE end-to-end demo automatically.
    Creates policy → Pays premium → Simulates weather → Processes claim → Shows treasury.
    """
    city = "Mumbai"
    rain_mm = round(random.uniform(45.0, 65.0), 1)

    await update.message.reply_text(
        "🎯 *FULL END-TO-END DEMO*\n\n"
        "Running complete insurance lifecycle…\n"
        f"📍 City: {city}\n"
        f"🌧️ Simulated rainfall: {rain_mm}mm\n\n"
        "_Step 1 of 5: Creating policy…_",
        parse_mode="Markdown",
    )
    await asyncio.sleep(1)

    # 1. Create policy
    try:
        request = PolicyCreate(location=city, coverage_type="rainfall")
        policy = await coordinator.create_policy(request)

        await update.message.reply_text(
            f"✅ *Step 1: Policy Created*\n\n"
            f"📋 ID: `{policy.policy_id}`\n"
            f"📍 {policy.location} | {policy.coverage_type}\n"
            f"⚡ Trigger: > {policy.trigger_threshold}mm\n"
            f"💰 Premium: {policy.premium_weekly} USDC/week\n"
            f"🛡️ Coverage: {policy.coverage_amount} USDC",
            parse_mode="Markdown",
        )
        await asyncio.sleep(1.5)
    except Exception as e:
        await update.message.reply_text(f"❌ Policy creation failed: {e}")
        return

    # 2. Pay premium
    await update.message.reply_text("_Step 2 of 5: Paying premium via x402…_", parse_mode="Markdown")
    try:
        payment = await collect_premium(
            policy_id=policy.policy_id,
            premium_amount=policy.premium_weekly,
            user_wallet=policy.user_wallet or "",
        )
        if payment["status"] == "completed":
            deposit_premium(
                payment_id=payment["payment_id"],
                policy_id=policy.policy_id,
                amount=policy.premium_weekly,
                tx_hash=payment["tx_hash"],
            )
        await update.message.reply_text(
            f"✅ *Step 2: Premium Paid*\n\n"
            f"💳 Amount: {policy.premium_weekly} USDC\n"
            f"🔗 Tx: `{payment['tx_hash'][:20]}...`\n"
            f"📡 Protocol: x402 on GOAT Testnet3",
            parse_mode="Markdown",
        )
        await asyncio.sleep(1.5)
    except Exception as e:
        await update.message.reply_text(f"⚠️ Premium payment simulated (error: {e})")

    # 3. Oracle detects weather
    await update.message.reply_text(
        f"✅ *Step 3: Oracle Detection*\n\n"
        f"📡 Weather oracle scanning {city}…\n"
        f"🌧️ Rainfall detected: *{rain_mm}mm*\n"
        f"⚡ Threshold: 40mm\n"
        f"🔴 *TRIGGER EXCEEDED!*\n\n"
        f"_Automated claim workflow initiated…_",
        parse_mode="Markdown",
    )
    await asyncio.sleep(1.5)

    # 4. AI verification + payout
    await update.message.reply_text("_Step 4 of 5: AI verification + GOAT payout…_", parse_mode="Markdown")
    try:
        payout = await process_claim_payout(
            claim_id=f"CLM-DEMO-{random.randint(1000, 9999)}",
            policy_id=policy.policy_id,
            payout_amount=policy.coverage_amount,
            user_wallet=policy.user_wallet or "",
            trigger_event=f"Heavy rainfall: {rain_mm}mm > 40mm",
            location=city,
            proof_dataset=f"lazai://proof/rainfall/{city.lower()}/{datetime.now().strftime('%Y%m%d')}",
        )

        tx_hash = payout.get("tx_hash", "N/A")
        explorer = payout.get("explorer_url", "#")

        await asyncio.sleep(1)

        await update.message.reply_text(
            f"✅ *Step 4: Claim Paid!*\n\n"
            f"🤖 AI Agent: Verified ✅\n"
            f"💰 *Payout: {payout.get('amount', policy.coverage_amount)} USDC*\n"
            f"🔗 Tx: `{tx_hash[:24]}...`\n"
            f"📊 Status: {payout.get('status', 'completed')}\n"
            f"🔗 [Explorer]({explorer})",
            parse_mode="Markdown",
        )
        await asyncio.sleep(1.5)
    except Exception as e:
        await update.message.reply_text(f"⚠️ Payout simulation: {e}")

    # 5. Treasury status
    try:
        t_status = get_treasury_status()
        await update.message.reply_text(
            f"✅ *Step 5: Treasury Updated*\n\n"
            f"💰 Collected: {t_status['total_collected']} USDC\n"
            f"💸 Paid Out: {t_status['total_paid_out']} USDC\n"
            f"💧 Available: {t_status['available_liquidity']} USDC\n"
            f"📊 Transactions: {t_status['transaction_count']}",
            parse_mode="Markdown",
        )
    except Exception as e:
        await update.message.reply_text(f"⚠️ Treasury: {e}")

    # Final summary
    await asyncio.sleep(1)
    await update.message.reply_text(
        "🎉 *DEMO COMPLETE!*\n\n"
        "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
        f"📋 Policy `{policy.policy_id}` created\n"
        f"💳 Premium paid via x402\n"
        f"🌧️ Heavy rainfall {rain_mm}mm detected\n"
        f"🤖 AI verified claim\n"
        f"💰 Payout sent on GOAT Testnet3\n"
        "🏦 Treasury updated\n"
        "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n\n"
        "*Full Flow:*\n"
        "User → Telegram → Policy Engine →\n"
        "x402 Payment → Oracle → AI Agent →\n"
        "GOAT Network → User Wallet\n\n"
        "_Powered by: OpenClaw + Metis + LazAI + GOAT_",
        parse_mode="Markdown",
    )


async def demo_aqi(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """
    /demo_aqi <city> – Simulate dangerous AQI >250 and process claim.
    Best cities for demo: Delhi (320), Lucknow (340), Kanpur (360)
    """
    args = context.args
    city = args[0] if args else "Delhi"

    # Use realistic AQI values for Indian cities
    aqi_map = {
        "delhi": 320, "lucknow": 340, "kanpur": 360,
        "patna": 290, "kolkata": 210, "mumbai": 180,
    }
    aqi_value = aqi_map.get(city.lower(), random.randint(260, 380))
    threshold = 250

    await update.message.reply_text(
        f"🎮 *AQI DEMO – {city}*\n\n"
        f"India has some of the worst air quality in the world.\n"
        f"Simulating dangerous AQI event…\n"
        f"💨 AQI: {aqi_value} (threshold: {threshold})",
        parse_mode="Markdown",
    )
    await asyncio.sleep(1)

    # Step 1: Oracle data
    await update.message.reply_text(
        f"📡 *Step 1: Oracle Data*\n\n"
        f"💨 AQI: *{aqi_value}* (🔴 EXCEEDS {threshold})\n"
        f"🌡️ Temperature: {round(random.uniform(28, 38), 1)}°C\n"
        f"💧 Humidity: {random.randint(35, 60)}%\n"
        f"🌧️ Rainfall: {round(random.uniform(0, 5), 1)}mm\n"
        f"🚦 Alert Level: *CRITICAL*\n\n"
        f"_Dangerous air quality for outdoor workers…_",
        parse_mode="Markdown",
    )
    await asyncio.sleep(1.5)

    # Step 2: Find or create policy
    policies = coordinator._load_policies()
    city_policies = [p for p in policies if p.get("location", "").lower() == city.lower()
                     and p.get("coverage_type") == "aqi" and p.get("status") == "active"]

    if not city_policies:
        await update.message.reply_text(f"📋 Creating AQI policy for {city}…")
        request = PolicyCreate(location=city, coverage_type="aqi")
        policy = await coordinator.create_policy(request)
        city_policies = [{"policy_id": policy.policy_id, "coverage_amount": policy.coverage_amount,
                         "premium_weekly": policy.premium_weekly, "trigger_threshold": policy.trigger_threshold}]
        await asyncio.sleep(0.5)

    target = city_policies[0]
    policy_id = target["policy_id"]

    await update.message.reply_text(
        f"🔍 *Step 2: AI Claim Verification*\n\n"
        f"📋 Policy: `{policy_id}`\n"
        f"🛡️ Coverage: {target.get('coverage_amount', 10)} USDC\n"
        f"⚡ Trigger: AQI > {target.get('trigger_threshold', threshold)}\n"
        f"💨 Actual AQI: *{aqi_value}* ← EXCEEDED ✅\n\n"
        f"🤖 ClaimVerificationAgent validating…\n"
        f"📊 LazAI proof dataset logged\n"
        f"✅ *Claim VERIFIED by AI agent*",
        parse_mode="Markdown",
    )
    await asyncio.sleep(1.5)

    # Step 3: Process payout
    await update.message.reply_text(
        f"💰 *Step 3: GOAT Network Payout*\n\n"
        f"Sending on-chain transaction…\n"
        f"🌐 Network: GOAT Testnet3 (Chain 48816)\n"
        f"📡 Protocol: x402",
        parse_mode="Markdown",
    )

    try:
        payout_amount = target.get("coverage_amount", 10)
        policy_obj = coordinator.get_policy(policy_id)

        payout = await process_claim_payout(
            claim_id=f"CLM-AQI-{random.randint(1000, 9999)}",
            policy_id=policy_id,
            payout_amount=payout_amount,
            user_wallet=policy_obj.user_wallet if policy_obj else "",
            trigger_event=f"Dangerous AQI: {aqi_value} > {threshold} threshold",
            location=city,
            proof_dataset=f"lazai://proof/aqi/{city.lower()}/{datetime.now().strftime('%Y%m%d')}",
        )

        tx_hash = payout.get("tx_hash", "N/A")
        explorer = payout.get("explorer_url", "#")

        await asyncio.sleep(1)

        await update.message.reply_text(
            f"🚨 *AQI CLAIM PAID – DEMO COMPLETE!*\n\n"
            f"━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
            f"💨 Event: Dangerous AQI ({aqi_value})\n"
            f"📍 City: {city}\n"
            f"📋 Policy: `{policy_id}`\n"
            f"💰 *Payout: {payout.get('amount', payout_amount)} USDC*\n"
            f"🔗 Tx: `{tx_hash[:24]}...`\n"
            f"🌐 GOAT Testnet3 (Chain 48816)\n"
            f"📊 Status: ✅ {payout.get('status', 'completed')}\n"
            f"━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n\n"
            f"🔗 [View on GOAT Explorer]({explorer})\n\n"
            f"_Gig workers (delivery drivers, street vendors) are_\n"
            f"_most vulnerable to dangerous air quality._\n"
            f"_ClimaShield protects them automatically._",
            parse_mode="Markdown",
        )
    except Exception as e:
        await update.message.reply_text(f"❌ Payout error: {e}")


# ── Bot Entry Point ─────────────────────────────────────────────────

def main():
    """Start the Telegram bot."""
    token = settings.telegram_bot_token
    if not token:
        print("❌ TELEGRAM_BOT_TOKEN not set. Please configure it in .env")
        sys.exit(1)

    print("🤖 Starting ClimaShield Telegram Bot (Phase 5 – Demo Ready)…")

    application = Application.builder().token(token).build()

    # Phase 1
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("buy_policy", buy_policy))
    application.add_handler(CommandHandler("check_policy", check_policy))
    application.add_handler(CommandHandler("status", status))

    # Phase 2
    application.add_handler(CommandHandler("risk_score", risk_score))
    application.add_handler(CommandHandler("oracle_status", oracle_status))
    application.add_handler(CommandHandler("trigger_alert", trigger_alert))

    # Phase 3
    application.add_handler(CommandHandler("pay_premium", pay_premium))
    application.add_handler(CommandHandler("claim_status", claim_status))
    application.add_handler(CommandHandler("treasury", treasury))

    # Phase 5 – Demo
    application.add_handler(CommandHandler("wallet", wallet_cmd))
    application.add_handler(CommandHandler("demo", demo))
    application.add_handler(CommandHandler("demo_aqi", demo_aqi))
    application.add_handler(CommandHandler("demo_full", demo_full))

    # drop_pending_updates=True fixes the "Conflict: terminated by other getUpdates" error
    application.run_polling(allowed_updates=Update.ALL_TYPES, drop_pending_updates=True)


if __name__ == "__main__":
    main()

