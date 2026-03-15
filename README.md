# 🛡️ ClimaShield – AI Parametric Insurance Platform

> AI-powered parametric insurance protecting gig workers and farmers from environmental disruptions (rain, floods, extreme heat, pollution).

**Built with:** OpenClaw Agents • Metis AI Compute • LazAI Data Layer • x402 Payments • GOAT Testnet3

---

## 🏗️ Architecture

```
┌──────────────────────────────────────────────────────────────────┐
│                    ClimaShield System (Phase 4)                  │
│                                                                  │
│  ┌──────────────┐  ┌────────────────┐  ┌──────────────────────┐ │
│  │  Telegram Bot │  │  FastAPI (22   │  │  Background Worker   │ │
│  │  (10 cmds)    │  │   Endpoints)   │  │  (5-min oracle)      │ │
│  └──────┬───────┘  └───────┬────────┘  └──────────┬───────────┘ │
│         │                  │                       │             │
│  ┌──────▼──────────────────▼───────────────────────▼───────────┐ │
│  │              CoordinatorAgent (OpenClaw)                    │ │
│  │  ┌───────────┐  ┌──────────┐  ┌────────────────────┐      │ │
│  │  │ Weather   │  │ Risk     │  │ Claim Verification │      │ │
│  │  │ Oracle    │  │ Engine   │  │ + Auto Payout      │      │ │
│  │  └─────┬─────┘  └────┬─────┘  └────────┬───────────┘      │ │
│  └────────│──────────────│─────────────────│──────────────────┘ │
│           │              │                 │                     │
│  ┌────────▼──────┐ ┌─────▼──────┐ ┌───────▼────────────┐      │
│  │ OpenWeather   │ │ Metis AI   │ │ x402 + GOAT Wallet │      │
│  │ API           │ │ Compute    │ │ Payments            │      │
│  └───────────────┘ └────────────┘ └─────────────────────┘      │
│           │                               │                     │
│  ┌────────▼──────┐               ┌────────▼────────┐           │
│  │ LazAI Dataset │               │ GOAT Testnet3   │           │
│  │ (Proofs)      │               │ (Settlements)   │           │
│  └───────────────┘               └─────────────────┘           │
└──────────────────────────────────────────────────────────────────┘
```

---

## 📂 Project Structure

```
climashield/
├── app/
│   ├── agents/         # OpenClaw agents
│   ├── api/routes.py   # 22 API endpoints
│   ├── models/         # Pydantic models
│   ├── services/       # Risk, identity, logging, scheduler
│   ├── config.py       # Environment configuration
│   └── main.py         # FastAPI app with lifecycle
├── ai/                 # AI risk model, prediction, anomaly detection
├── oracle/             # Oracle monitor + validator
├── lazai/              # LazAI verifiable data storage
├── payments/           # x402 client, GOAT wallet, treasury, payouts
├── workers/            # Background oracle worker
├── simulation/         # Weather event simulator
├── telegram/           # Telegram bot (10 commands)
├── tests/              # Test suite
├── data/               # JSON stores (policies, treasury, datasets)
├── logs/               # System + event logs
├── Dockerfile          # Production container
├── docker-compose.yml  # Multi-service deployment
└── requirements.txt    # Python dependencies
```

---

## 🚀 Quick Start

```bash
# 1. Clone and setup
git clone <repo>
cd ClimaShield
cp .env.example .env  # Edit with your API keys

# 2. Install
pip install -r requirements.txt

# 3. Run API server
uvicorn app.main:app --reload --port 8000

# 4. Run Telegram bot (separate terminal)
python telegram/bot.py

# 5. Test
pytest tests/ -v
```

### Docker

```bash
docker build -t climashield .
docker run -p 8000:8000 --env-file .env climashield

# Or with docker-compose (API + Bot)
docker-compose up -d
```

---

## 📡 API Endpoints (22 total)

### Health & Monitoring
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/health` | Health check with agent status + scheduler |
| GET | `/logs/recent` | Recent system event logs |
| GET | `/logs/summary` | Event summary by category |
| GET | `/scheduler/status` | Background job status |

### Policies
| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/policy/create` | Create parametric policy |
| GET | `/policies` | List all policies |
| GET | `/policy/{id}` | Get policy details |
| POST | `/policy/cancel` | Cancel a policy |
| POST | `/policy/check-trigger` | Check triggers for policy |

### Oracle & Risk
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/oracle/latest` | Latest oracle events |
| GET | `/oracle/history/{city}` | City oracle history |
| POST | `/oracle/check-triggers` | Monitor all policies |
| GET | `/risk/{city}` | AI risk assessment |

### Payments & Claims
| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/payments/create-premium` | Pay premium via x402 |
| POST | `/payments/verify` | Verify payment |
| POST | `/claims/process` | Process claim + payout |
| GET | `/claims/history` | Claim event history |
| GET | `/treasury/status` | Treasury pool status |

### Simulation & Workers
| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/simulate/rainfall` | Simulate heavy rain |
| POST | `/simulate/heat` | Simulate extreme heat |
| POST | `/simulate/pollution` | Simulate pollution |
| POST | `/simulate/flood` | Simulate flood alert |
| POST | `/worker/run-cycle` | Manual oracle cycle |

### Identity
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/agent/identity` | ERC-8004 agent identity |

---

## 🤖 Telegram Commands (10 total)

| Command | Description |
|---------|-------------|
| `/start` | Welcome + help |
| `/buy_policy <city> <type>` | Create policy |
| `/check_policy <id>` | Check triggers |
| `/status <id>` | View policy |
| `/risk_score <city>` | AI risk assessment |
| `/oracle_status <city>` | Live weather oracle |
| `/trigger_alert <city>` | Check active alerts |
| `/pay_premium <id>` | Pay via x402 |
| `/claim_status <id>` | Process claim + payout |
| `/treasury` | Treasury pool status |

---

## ⚙️ Environment Variables

```env
WEATHER_API_KEY=         # OpenWeatherMap API key
TELEGRAM_BOT_TOKEN=      # Telegram bot token
ERC8004_AGENT_ID=200     # Agent identity
ERC8004_REGISTRY=0x...   # ERC-8004 registry
GOATX402_API_URL=        # x402 payment API
GOATX402_MERCHANT_ID=    # Merchant ID
GOATX402_API_KEY=        # x402 API key
GOATX402_API_SECRET=     # x402 API secret
RECEIVE_WALLET=0x...     # Treasury wallet
GOAT_RPC_URL=            # GOAT Testnet3 RPC
GOAT_CHAIN_ID=48816      # Chain ID
```

---

## 🧪 Testing

```bash
# Run all tests
pytest tests/ -v

# Run specific test
pytest tests/test_policy.py -v
pytest tests/test_oracle.py -v
pytest tests/test_payments.py -v

# Test simulation via API
curl -X POST http://localhost:8000/simulate/rainfall \
  -H "Content-Type: application/json" \
  -d '{"city":"Mumbai","value":45}'

# Manual oracle worker cycle
curl -X POST http://localhost:8000/worker/run-cycle
```

---

## 📊 Phase Summary

| Phase | Features | Status |
|-------|----------|--------|
| **1** | Agents, FastAPI, Telegram, policies, weather API | ✅ |
| **2** | AI risk engine, oracle monitoring, LazAI storage | ✅ |
| **3** | x402 payments, GOAT wallet, treasury, payouts | ✅ |
| **4** | Background workers, simulation, logging, Docker, tests | ✅ |
