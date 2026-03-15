"use client";

import { useEffect, useState } from "react";
import MetricCard from "@/components/cards/MetricCard";
import { Shield, Droplets, Thermometer, Wind, CreditCard } from "lucide-react";
import { getPolicies, getOracleLatest, getTreasuryStatus, getWalletBalance } from "@/services/api";

export default function UserDashboard() {
  const [policies, setPolicies] = useState<any[]>([]);
  const [oracle, setOracle] = useState<any>(null);
  const [treasury, setTreasury] = useState<any>(null);
  const [wallet, setWallet] = useState<any>(null);

  useEffect(() => {
    const load = async () => {
      try {
        const [p, o, t, w] = await Promise.all([
          getPolicies(), getOracleLatest().catch(() => null),
          getTreasuryStatus().catch(() => null),
          getWalletBalance().catch(() => null),
        ]);
        setPolicies(p.policies || []);
        setOracle(o);
        setTreasury(t);
        setWallet(w);
      } catch {}
    };
    load();
    const id = setInterval(load, 20000);
    return () => clearInterval(id);
  }, []);

  const activePolicies = policies.filter((p: any) => p.status === "active");
  const totalCoverage = activePolicies.reduce((s: number, p: any) => s + (p.coverage_amount || 0), 0);

  return (
    <div className="space-y-8 animate-in">
      {/* Header */}
      <div>
        <h1 className="text-2xl font-bold">Farm Overview</h1>
        <p className="text-gray-500 text-sm mt-1">Your insurance coverage & weather monitoring</p>
      </div>

      {/* Metric Cards */}
      <div className="grid grid-cols-2 lg:grid-cols-4 gap-4">
        <MetricCard label="Active Policies" value={activePolicies.length} sub={`of ${policies.length} total`} icon={Shield} color="emerald" />
        <MetricCard label="Coverage Amount" value={`₹${totalCoverage.toLocaleString()}`} icon={CreditCard} color="cyan" />
        <MetricCard label="Next Payment" value={activePolicies[0]?.premium_weekly ? `${activePolicies[0].premium_weekly} USDC` : "—"} sub="Weekly premium" icon={CreditCard} color="amber" />
        {wallet && (
          <MetricCard label="Wallet Balance" value={`${wallet.balance_btc?.toFixed(6)} BTC`} sub={wallet.real_balance ? "🟢 Connected" : "⚪ Simulated"} icon={Shield} color="cyan" />
        )}
      </div>

      {/* Weather Risk Monitor */}
      <div className="bg-[#0f1420] border border-white/5 rounded-xl p-6">
        <h3 className="text-sm font-semibold text-gray-300 mb-6">🌤️ Weather Risk Monitor</h3>
        <div className="grid grid-cols-3 gap-6">
          {/* Rainfall Gauge */}
          <div className="text-center">
            <div className="relative w-28 h-28 mx-auto mb-3">
              <svg viewBox="0 0 120 120" className="w-full h-full -rotate-90">
                <circle cx="60" cy="60" r="50" fill="none" stroke="rgba(255,255,255,0.05)" strokeWidth="10" />
                <circle cx="60" cy="60" r="50" fill="none" stroke="#22d3ee" strokeWidth="10" strokeDasharray={`${Math.min(40, 40) * 3.14} 314`} strokeLinecap="round" />
              </svg>
              <div className="absolute inset-0 flex items-center justify-center">
                <Droplets className="w-6 h-6 text-cyan-400" />
              </div>
            </div>
            <div className="text-sm font-medium">Rainfall</div>
            <div className="text-xs text-gray-500">Normal</div>
          </div>

          {/* Temperature Gauge */}
          <div className="text-center">
            <div className="relative w-28 h-28 mx-auto mb-3">
              <svg viewBox="0 0 120 120" className="w-full h-full -rotate-90">
                <circle cx="60" cy="60" r="50" fill="none" stroke="rgba(255,255,255,0.05)" strokeWidth="10" />
                <circle cx="60" cy="60" r="50" fill="none" stroke="#fbbf24" strokeWidth="10" strokeDasharray={`${Math.min(70, 100) * 3.14} 314`} strokeLinecap="round" />
              </svg>
              <div className="absolute inset-0 flex items-center justify-center">
                <Thermometer className="w-6 h-6 text-amber-400" />
              </div>
            </div>
            <div className="text-sm font-medium">Temperature</div>
            <div className="text-xs text-gray-500">Moderate</div>
          </div>

          {/* AQI Gauge */}
          <div className="text-center">
            <div className="relative w-28 h-28 mx-auto mb-3">
              <svg viewBox="0 0 120 120" className="w-full h-full -rotate-90">
                <circle cx="60" cy="60" r="50" fill="none" stroke="rgba(255,255,255,0.05)" strokeWidth="10" />
                <circle cx="60" cy="60" r="50" fill="none" stroke="#34d399" strokeWidth="10" strokeDasharray={`${Math.min(30, 100) * 3.14} 314`} strokeLinecap="round" />
              </svg>
              <div className="absolute inset-0 flex items-center justify-center">
                <Wind className="w-6 h-6 text-emerald-400" />
              </div>
            </div>
            <div className="text-sm font-medium">Air Quality</div>
            <div className="text-xs text-gray-500">Good</div>
          </div>
        </div>
      </div>

      {/* Active Policies Table */}
      {policies.length > 0 && (
        <div className="bg-[#0f1420] border border-white/5 rounded-xl overflow-hidden">
          <div className="px-6 py-4 border-b border-white/5">
            <h3 className="text-sm font-semibold text-gray-300">📋 Your Policies</h3>
          </div>
          <div className="overflow-x-auto">
            <table className="w-full">
              <thead>
                <tr className="border-b border-white/5">
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Policy ID</th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">City</th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Coverage</th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Premium</th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Amount</th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Status</th>
                </tr>
              </thead>
              <tbody>
                {policies.map((p: any) => (
                  <tr key={p.policy_id} className="border-b border-white/5 hover:bg-white/[0.02]">
                    <td className="px-6 py-3 text-sm font-mono text-emerald-400">{p.policy_id}</td>
                    <td className="px-6 py-3 text-sm">{p.location}</td>
                    <td className="px-6 py-3 text-sm capitalize">{p.coverage_type}</td>
                    <td className="px-6 py-3 text-sm">{p.premium_weekly} USDC</td>
                    <td className="px-6 py-3 text-sm">{p.coverage_amount} USDC</td>
                    <td className="px-6 py-3">
                      <span className={`px-2.5 py-0.5 rounded-full text-xs font-medium ${
                        p.status === "active" ? "bg-emerald-500/10 text-emerald-400" : "bg-red-500/10 text-red-400"
                      }`}>{p.status}</span>
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
