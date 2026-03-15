#!/bin/bash
# ClimaShield Deployment Script
# Usage: ./deploy.sh [local|docker|production]

set -e

MODE=${1:-local}

echo "🛡️  ClimaShield Deployment"
echo "========================="
echo "Mode: $MODE"
echo ""

case $MODE in
  local)
    echo "📦 Installing dependencies..."
    pip install -r requirements.txt

    echo "💾 Initializing database..."
    python -c "from app.db.database import init_db; init_db(); print('✅ Database ready')"

    echo "🌱 Seeding data..."
    curl -s -X POST http://localhost:8000/admin/seed-db 2>/dev/null || true

    echo "🚀 Starting API server..."
    uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
    ;;

  docker)
    echo "🐳 Building and starting Docker containers..."
    docker-compose up --build -d

    echo "⏳ Waiting for services..."
    sleep 10

    echo "🌱 Seeding database..."
    curl -s -X POST http://localhost:8000/admin/seed-db | python3 -m json.tool

    echo ""
    echo "✅ ClimaShield is running!"
    echo "  📡 API:       http://localhost:8000"
    echo "  📡 API Docs:  http://localhost:8000/docs"
    echo "  💾 Database:  PostgreSQL on port 5432"
    echo "  🤖 Bot:       Running in container"
    echo ""
    echo "📊 Dashboard: http://localhost:8000/admin/metrics"
    echo ""
    echo "To stop: docker-compose down"
    ;;

  production)
    echo "🌍 Production deployment checklist:"
    echo ""
    echo "  1. Set up PostgreSQL (Render/Railway/Supabase)"
    echo "  2. Set DATABASE_URL in environment"
    echo "  3. Deploy backend: render.com or railway.app"
    echo "  4. Deploy frontend: vercel.com"
    echo "  5. Set API_URL for Telegram bot"
    echo "  6. Configure GOAT_PRIVATE_KEY securely"
    echo ""
    echo "Backend deployment (Render):"
    echo "  - Build command: pip install -r requirements.txt"
    echo "  - Start command: uvicorn app.main:app --host 0.0.0.0 --port \$PORT"
    echo ""
    echo "Frontend deployment (Vercel):"
    echo "  - cd frontend && npx vercel"
    echo "  - Set NEXT_PUBLIC_API_URL to your backend URL"
    ;;

  test)
    echo "🧪 Running E2E tests..."
    echo ""

    BASE="http://localhost:8000"

    echo "1. Health check..."
    curl -sf "$BASE/health" | python3 -c "import sys,json; d=json.load(sys.stdin); print(f'   ✅ v{d[\"version\"]} – {len(d[\"agents\"])} agents')"

    echo "2. Admin metrics..."
    curl -sf "$BASE/admin/metrics" | python3 -c "import sys,json; d=json.load(sys.stdin); print(f'   ✅ {d[\"active_policies\"]} policies, {d[\"total_premiums\"]} premiums, {d[\"profit\"]} profit')"

    echo "3. City stats..."
    curl -sf "$BASE/admin/city-stats" | python3 -c "import sys,json; d=json.load(sys.stdin); print(f'   ✅ {len(d)} cities')"

    echo "4. Treasury..."
    curl -sf "$BASE/admin/treasury" | python3 -c "import sys,json; d=json.load(sys.stdin); print(f'   ✅ Balance: {d[\"current_balance\"]} USDC, Margin: {d[\"profit_margin\"]}%')"

    echo "5. Wallet balance..."
    curl -sf "$BASE/wallet/balance" | python3 -c "import sys,json; d=json.load(sys.stdin); print(f'   ✅ {d[\"balance_btc\"]} BTC (real: {d[\"real_balance\"]})')"

    echo "6. Create policy..."
    curl -sf -X POST "$BASE/policy/create" -H "Content-Type: application/json" \
      -d '{"location":"TestDeploy","coverage_type":"rainfall"}' | \
      python3 -c "import sys,json; d=json.load(sys.stdin); print(f'   ✅ Created {d[\"policy\"][\"policy_id\"]}')"

    echo "7. Simulate rainfall..."
    curl -sf -X POST "$BASE/simulate/rainfall" -H "Content-Type: application/json" \
      -d '{"city":"TestDeploy","value":50}' | \
      python3 -c "import sys,json; d=json.load(sys.stdin); print(f'   ✅ {d[\"claims_triggered\"]} claims triggered')"

    echo "8. Policies list..."
    curl -sf "$BASE/policies" | python3 -c "import sys,json; d=json.load(sys.stdin); print(f'   ✅ {d[\"total\"]} total policies')"

    echo "9. Scheduler..."
    curl -sf "$BASE/scheduler/status" | python3 -c "import sys,json; d=json.load(sys.stdin); print(f'   ✅ Running: {d[\"running\"]}, Jobs: {len(d[\"jobs\"])}')"

    echo "10. Worker cycle..."
    curl -sf -X POST "$BASE/worker/run-cycle" | python3 -c "import sys,json; d=json.load(sys.stdin); print(f'   ✅ {d[\"cities_monitored\"]} cities, {d[\"policies_checked\"]} policies')"

    echo ""
    echo "🎉 All E2E tests passed!"
    ;;

  *)
    echo "Usage: ./deploy.sh [local|docker|production|test]"
    exit 1
    ;;
esac
