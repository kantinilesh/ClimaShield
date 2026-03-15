"use client";

import { useEffect, useState } from "react";
import MetricCard from "@/components/cards/MetricCard";
import {
  FileText, DollarSign, AlertTriangle, TrendingUp,
  Zap, Wallet,
} from "lucide-react";
import { getMetrics, getCityStats, getTreasury, getWalletBalance } from "@/services/api";
import {
  AreaChart, Area, XAxis, YAxis, CartesianGrid, Tooltip,
  ResponsiveContainer, PieChart, Pie, Cell,
} from "recharts";

const COLORS = ["#34d399", "#f87171", "#fbbf24", "#22d3ee", "#a78bfa"];

export default function AdminDashboard() {
  const [metrics, setMetrics] = useState<any>(null);
  const [cities, setCities] = useState<any[]>([]);
  const [treasury, setTreasury] = useState<any>(null);
  const [wallet, setWallet] = useState<any>(null);

  useEffect(() => {
    const load = async () => {
      try {
        const [m, c, t, w] = await Promise.all([
          getMetrics(), getCityStats(), getTreasury(),
          getWalletBalance().catch(() => null),
        ]);
        setMetrics(m);
        setCities(c);
        setTreasury(t);
        setWallet(w);
      } catch {}
    };
    load();
    const id = setInterval(load, 15000);
    return () => clearInterval(id);
  }, []);

  if (!metrics) {
    return (
      <div className="flex items-center justify-center h-[60vh]">
        <div className="text-gray-500 animate-pulse text-lg">Loading dashboard…</div>
      </div>
    );
  }

  const chartData = cities.map((c) => ({
    name: c.city,
    policies: c.active_policies,
    claims: c.claims,
  }));

  const pieData = cities.map((c) => ({
    name: c.city,
    value: c.active_policies,
  }));

  return (
    <div className="space-y-8 animate-in">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold">Company Analytics</h1>
          <p className="text-gray-500 text-sm mt-1">Real-time insurance operations dashboard</p>
        </div>
        <div className="flex items-center gap-2 text-xs text-gray-500">
          <span className="w-2 h-2 rounded-full bg-emerald-400 animate-pulse" />
          Live • Auto-refresh 15s
        </div>
      </div>

      {/* Metric Cards */}
      <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-6 gap-4">
        <MetricCard label="Active Policies" value={metrics.active_policies} sub={`of ${metrics.total_policies} total`} icon={FileText} color="emerald" />
        <MetricCard label="Total Premiums" value={`${metrics.total_premiums} USDC`} sub={`${metrics.payment_count} payments`} icon={DollarSign} color="cyan" />
        <MetricCard label="Claims Paid" value={`${metrics.claims_paid} USDC`} sub={`${metrics.claims_count} claims`} icon={AlertTriangle} color="red" />
        <MetricCard label="Profit / Loss" value={`${metrics.profit >= 0 ? "+" : ""}${metrics.profit} USDC`} icon={TrendingUp} color={metrics.profit >= 0 ? "emerald" : "red"} />
        <MetricCard label="Oracle Triggers" value={metrics.oracle_triggers} sub={`${metrics.oracle_events_total} total events`} icon={Zap} color="amber" />
        {wallet && (
          <MetricCard label="Wallet (GOAT)" value={`${wallet.balance_btc?.toFixed(6)} BTC`} sub={wallet.real_balance ? "🟢 Real" : "⚪ Sim"} icon={Wallet} color="cyan" />
        )}
      </div>

      {/* Charts Row */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Treasury Panel */}
        {treasury && (
          <div className="lg:col-span-1 bg-[#0f1420] border border-emerald-500/10 rounded-xl p-6">
            <h3 className="text-sm font-semibold text-emerald-400 mb-4">🏦 Treasury & Liquidity</h3>
            <div className="space-y-4">
              <div className="flex justify-between items-center">
                <span className="text-gray-500 text-sm">Premium Pool</span>
                <span className="text-emerald-400 font-bold">{treasury.premium_pool} USDC</span>
              </div>
              <div className="w-full bg-white/5 rounded-full h-2">
                <div className="bg-emerald-500 h-2 rounded-full" style={{ width: `${Math.min(100, treasury.profit_margin)}%` }} />
              </div>
              <div className="flex justify-between items-center">
                <span className="text-gray-500 text-sm">Claims Paid</span>
                <span className="text-red-400 font-bold">{treasury.claims_paid} USDC</span>
              </div>
              <div className="flex justify-between items-center">
                <span className="text-gray-500 text-sm">Balance</span>
                <span className="text-white font-bold">{treasury.current_balance} USDC</span>
              </div>
              <div className="pt-3 border-t border-white/5 flex justify-between items-center">
                <span className="text-gray-500 text-sm">Profit Margin</span>
                <span className={`font-bold text-lg ${treasury.profit >= 0 ? "text-emerald-400" : "text-red-400"}`}>
                  {treasury.profit_margin}%
                </span>
              </div>
            </div>
          </div>
        )}

        {/* Area Chart: Policies vs Claims by city */}
        <div className="lg:col-span-2 bg-[#0f1420] border border-white/5 rounded-xl p-6">
          <h3 className="text-sm font-semibold text-gray-300 mb-4">Policies vs Claims by City</h3>
          <ResponsiveContainer width="100%" height={220}>
            <AreaChart data={chartData}>
              <defs>
                <linearGradient id="gPolicies" x1="0" y1="0" x2="0" y2="1">
                  <stop offset="5%" stopColor="#34d399" stopOpacity={0.3} />
                  <stop offset="95%" stopColor="#34d399" stopOpacity={0} />
                </linearGradient>
                <linearGradient id="gClaims" x1="0" y1="0" x2="0" y2="1">
                  <stop offset="5%" stopColor="#f87171" stopOpacity={0.3} />
                  <stop offset="95%" stopColor="#f87171" stopOpacity={0} />
                </linearGradient>
              </defs>
              <CartesianGrid strokeDasharray="3 3" stroke="rgba(255,255,255,0.04)" />
              <XAxis dataKey="name" tick={{ fill: "#6b7280", fontSize: 12 }} axisLine={false} />
              <YAxis tick={{ fill: "#6b7280", fontSize: 12 }} axisLine={false} />
              <Tooltip contentStyle={{ background: "#0f1420", border: "1px solid rgba(255,255,255,0.1)", borderRadius: "8px", color: "#fff" }} />
              <Area type="monotone" dataKey="policies" stroke="#34d399" fill="url(#gPolicies)" strokeWidth={2} />
              <Area type="monotone" dataKey="claims" stroke="#f87171" fill="url(#gClaims)" strokeWidth={2} />
            </AreaChart>
          </ResponsiveContainer>
        </div>
      </div>

      {/* City Stats Table */}
      {cities.length > 0 && (
        <div className="bg-[#0f1420] border border-white/5 rounded-xl overflow-hidden">
          <div className="px-6 py-4 border-b border-white/5">
            <h3 className="text-sm font-semibold text-gray-300">📍 City Risk Distribution</h3>
          </div>
          <div className="overflow-x-auto">
            <table className="w-full">
              <thead>
                <tr className="border-b border-white/5">
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">City</th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Active</th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Total</th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Claims</th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Risk</th>
                </tr>
              </thead>
              <tbody>
                {cities.map((c, i) => (
                  <tr key={c.city} className="border-b border-white/5 hover:bg-white/[0.02]">
                    <td className="px-6 py-3 text-sm font-medium">{c.city}</td>
                    <td className="px-6 py-3 text-sm text-emerald-400">{c.active_policies}</td>
                    <td className="px-6 py-3 text-sm text-gray-400">{c.total_policies}</td>
                    <td className="px-6 py-3 text-sm text-red-400">{c.claims}</td>
                    <td className="px-6 py-3">
                      <div className="w-16 bg-white/5 rounded-full h-1.5">
                        <div className="bg-amber-400 h-1.5 rounded-full" style={{ width: `${Math.min(100, (c.claims / Math.max(c.active_policies, 1)) * 100 + 20)}%` }} />
                      </div>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      )}
    </div>
  );
}
