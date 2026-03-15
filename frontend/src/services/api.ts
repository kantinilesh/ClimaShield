import axios from "axios";

const API_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

const api = axios.create({
  baseURL: API_URL,
  timeout: 15000,
  headers: { "Content-Type": "application/json" },
});

// ── Admin Analytics ──────────────────────────────────────────────
export const getMetrics = () => api.get("/admin/metrics").then((r) => r.data);
export const getCityStats = () => api.get("/admin/city-stats").then((r) => r.data);
export const getTreasury = () => api.get("/admin/treasury").then((r) => r.data);
export const getActivity = (limit = 20) => api.get(`/admin/activity?limit=${limit}`).then((r) => r.data);
export const getAdminPolicies = (status?: string) => api.get(`/admin/policies${status ? `?status=${status}` : ""}`).then((r) => r.data);
export const getAdminClaims = (status?: string) => api.get(`/admin/claims${status ? `?status=${status}` : ""}`).then((r) => r.data);
export const getAdminPayments = () => api.get("/admin/payments").then((r) => r.data);
export const getOracleEvents = (city?: string) => api.get(`/admin/oracle-events${city ? `?city=${city}` : ""}`).then((r) => r.data);

// ── Policies ─────────────────────────────────────────────────────
export const getPolicies = () => api.get("/policies").then((r) => r.data);
export const getPolicy = (id: string) => api.get(`/policy/${id}`).then((r) => r.data);
export const createPolicy = (data: { location: string; coverage_type: string }) =>
  api.post("/policy/create", data).then((r) => r.data);

// ── Payments & Claims ────────────────────────────────────────────
export const payPremium = (policy_id: string) =>
  api.post("/payments/create-premium", { policy_id }).then((r) => r.data);
export const processClaim = (policy_id: string) =>
  api.post("/claims/process", { policy_id }).then((r) => r.data);
export const getClaimsHistory = () => api.get("/claims/history").then((r) => r.data);

// ── Oracle / Weather ─────────────────────────────────────────────
export const getOracleLatest = () => api.get("/oracle/latest").then((r) => r.data);
export const getOracleHistory = (city: string) => api.get(`/oracle/history/${city}`).then((r) => r.data);
export const getRiskScore = (city: string) => api.get(`/risk/${city}`).then((r) => r.data);

// ── Treasury & Wallet ────────────────────────────────────────────
export const getTreasuryStatus = () => api.get("/treasury/status").then((r) => r.data);
export const getWalletBalance = () => api.get("/wallet/balance").then((r) => r.data);

// ── Health ───────────────────────────────────────────────────────
export const getHealth = () => api.get("/health").then((r) => r.data);

// ── Logs ─────────────────────────────────────────────────────────
export const getRecentLogs = (limit = 50) => api.get(`/logs/recent?limit=${limit}`).then((r) => r.data);
export const getLogsSummary = () => api.get("/logs/summary").then((r) => r.data);

// ── Simulation ───────────────────────────────────────────────────
export const simulateRainfall = (city: string, value = 50) =>
  api.post("/simulate/rainfall", { city, value }).then((r) => r.data);

export default api;
