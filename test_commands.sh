#!/bin/bash
# ═══════════════════════════════════════════════════════════════════
# ClimaShield – Local Test Commands
# Run these to verify all backend APIs, database, wallet, etc.
# 
# USAGE:
#   chmod +x test_commands.sh
#   ./test_commands.sh           # Run all tests
#   ./test_commands.sh health    # Run one section
# ═══════════════════════════════════════════════════════════════════

BASE="http://localhost:8000"
BOLD="\033[1m"
GREEN="\033[0;32m"
CYAN="\033[0;36m"
YELLOW="\033[0;33m"
NC="\033[0m"

header() { echo -e "\n${BOLD}${CYAN}══════════════════════════════════════${NC}"; echo -e "${BOLD}  $1${NC}"; echo -e "${CYAN}══════════════════════════════════════${NC}"; }
test_url() { echo -e "${YELLOW}→ $1${NC}"; curl -s "$BASE$2" | python3 -m json.tool 2>/dev/null || curl -s "$BASE$2"; echo ""; }

SECTION=${1:-all}

# ── 1. HEALTH & SYSTEM ─────────────────────────────────────────────
if [[ "$SECTION" == "all" || "$SECTION" == "health" ]]; then
    header "1. HEALTH & SYSTEM"
    test_url "Health Check" "/health"
    test_url "Agent Identity" "/agent/identity"
    test_url "Agent Capabilities" "/agent/capabilities"
fi

# ── 2. POLICIES ────────────────────────────────────────────────────
if [[ "$SECTION" == "all" || "$SECTION" == "policies" ]]; then
    header "2. POLICIES"
    test_url "List All Policies" "/policies"
    test_url "Get Policy CS1001" "/policy/CS1001"
    echo -e "${YELLOW}→ Create New Policy${NC}"
    curl -s -X POST "$BASE/policy/create" -H "Content-Type: application/json" \
      -d '{"location":"Delhi","coverage_type":"aqi"}' | python3 -m json.tool
    echo ""
fi

# ── 3. ORACLE & WEATHER ───────────────────────────────────────────
if [[ "$SECTION" == "all" || "$SECTION" == "oracle" ]]; then
    header "3. ORACLE & WEATHER"
    test_url "Oracle Latest (Mumbai)" "/oracle/latest?city=Mumbai"
    test_url "Oracle Latest (Delhi)" "/oracle/latest?city=Delhi"
    test_url "Oracle History (Mumbai)" "/oracle/history/Mumbai"
    test_url "Risk Score (Delhi)" "/risk/Delhi"
    test_url "Risk Score (Mumbai)" "/risk/Mumbai"
fi

# ── 4. PAYMENTS & TREASURY ────────────────────────────────────────
if [[ "$SECTION" == "all" || "$SECTION" == "payments" ]]; then
    header "4. PAYMENTS & TREASURY"
    test_url "Treasury Status" "/treasury/status"
fi

# ── 5. WALLET (GOAT NETWORK) ─────────────────────────────────────
if [[ "$SECTION" == "all" || "$SECTION" == "wallet" ]]; then
    header "5. GOAT WALLET"
    test_url "Wallet Balance (BTC)" "/wallet/balance"
fi

# ── 6. DATABASE (ADMIN) ──────────────────────────────────────────
if [[ "$SECTION" == "all" || "$SECTION" == "admin" ]]; then
    header "6. ADMIN / DATABASE"
    test_url "Admin Metrics" "/admin/metrics"
    test_url "City Statistics" "/admin/city-stats"
    test_url "Treasury Analytics" "/admin/treasury"
    test_url "Admin Policies" "/admin/policies"
    test_url "Admin Claims" "/admin/claims"
    test_url "Admin Payments" "/admin/payments"
    test_url "Oracle Events" "/admin/oracle-events"
    test_url "Recent Activity" "/admin/activity?limit=5"
fi

# ── 7. CLAIMS ─────────────────────────────────────────────────────
if [[ "$SECTION" == "all" || "$SECTION" == "claims" ]]; then
    header "7. CLAIMS"
    test_url "Claims History" "/claims/history"
fi

# ── 8. LOGS ───────────────────────────────────────────────────────
if [[ "$SECTION" == "all" || "$SECTION" == "logs" ]]; then
    header "8. SYSTEM LOGS"
    test_url "Recent Logs" "/logs/recent?limit=5"
    test_url "Log Summary" "/logs/summary"
fi

# ── 9. SIMULATION ─────────────────────────────────────────────────
if [[ "$SECTION" == "all" || "$SECTION" == "simulate" ]]; then
    header "9. SIMULATION"
    echo -e "${YELLOW}→ Simulate Rainfall (Mumbai, 55mm)${NC}"
    curl -s -X POST "$BASE/simulate/rainfall" -H "Content-Type: application/json" \
      -d '{"city":"Mumbai","value":55}' | python3 -m json.tool
    echo ""
fi

# ── 10. ENV & CONFIG CHECK ────────────────────────────────────────
if [[ "$SECTION" == "all" || "$SECTION" == "env" ]]; then
    header "10. ENVIRONMENT CHECK"
    echo -e "${YELLOW}→ .env file keys (masked):${NC}"
    if [ -f .env ]; then
        grep -v "^#" .env | grep -v "^$" | while IFS='=' read -r key value; do
            if [ -n "$key" ]; then
                masked=$(echo "$value" | sed 's/./*/g' | head -c 20)
                echo "  $key = ${masked}..."
            fi
        done
    else
        echo "  ⚠️  No .env file found"
    fi
    echo ""

    echo -e "${YELLOW}→ GOAT Private Key check:${NC}"
    if grep -q "GOAT_PRIVATE_KEY" .env 2>/dev/null; then
        echo "  ✅ GOAT_PRIVATE_KEY is set"
    else
        echo "  ❌ GOAT_PRIVATE_KEY is NOT set"
    fi

    echo -e "\n${YELLOW}→ Database file:${NC}"
    if [ -f "climashield.db" ]; then
        echo "  ✅ climashield.db exists ($(du -h climashield.db | cut -f1))"
        echo "  Tables:"
        sqlite3 climashield.db ".tables" 2>/dev/null || echo "  (sqlite3 not available)"
        echo "  Policy count:"
        sqlite3 climashield.db "SELECT COUNT(*) FROM policies;" 2>/dev/null || echo "  (sqlite3 not available)"
    else
        echo "  ⚠️  No SQLite database found (using JSON storage)"
    fi

    echo -e "\n${YELLOW}→ Policies JSON:${NC}"
    if [ -f "data/policies.json" ]; then
        count=$(python3 -c "import json; print(len(json.load(open('data/policies.json'))))" 2>/dev/null || echo "?")
        echo "  ✅ data/policies.json exists ($count policies)"
    else
        echo "  ⚠️  No policies.json found"
    fi
fi

header "DONE ✅"
echo -e "${GREEN}All tests completed! Check output above for any errors.${NC}\n"
