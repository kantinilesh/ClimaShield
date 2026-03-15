"use client";

import { useEffect, useState } from "react";
import { getTreasury, getWalletBalance } from "@/services/api";
import {
  PieChart, Pie, Cell, ResponsiveContainer, Tooltip,
} from "recharts";

const COLORS = ["#34d399", "#f87171"];

export default function AdminTreasury() {
  const [treasury, setTreasury] = useState<any>(null);
  const [wallet, setWallet] = useState<any>(null);

  useEffect(() => {
    const load = async () => {
      const [t, w] = await Promise.all([
        getTreasury().catch(() => null),
        getWalletBalance().catch(() => null),
      ]);
      setTreasury(t);
      setWallet(w);
    };
    load();
    const id = setInterval(load, 15000);
    return () => clearInterval(id);
  }, []);

  if (!treasury) return <div className="text-gray-500 animate-pulse p-8">Loading treasury…</div>;

  const pieData = [
    { name: "Balance", value: treasury.current_balance },
    { name: "Claims Paid", value: treasury.claims_paid },
  ];

  return (
    <div className="space-y-6 animate-in">
      <h1 className="text-2xl font-bold">Treasury Analytics</h1>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Donut Chart */}
        <div className="bg-[#0f1420] border border-emerald-500/10 rounded-xl p-6">
          <h3 className="text-sm font-semibold text-emerald-400 mb-4">Pool Distribution</h3>
          <ResponsiveContainer width="100%" height={250}>
            <PieChart>
              <Pie data={pieData} cx="50%" cy="50%" innerRadius={70} outerRadius={100} paddingAngle={4} dataKey="value">
                {pieData.map((_, i) => (
                  <Cell key={i} fill={COLORS[i]} />
                ))}
              </Pie>
              <Tooltip contentStyle={{ background: "#0f1420", border: "1px solid rgba(255,255,255,0.1)", borderRadius: "8px", color: "#fff" }} />
            </PieChart>
          </ResponsiveContainer>
          <div className="flex justify-center gap-6 mt-2">
            <span className="flex items-center gap-2 text-xs text-gray-400"><span className="w-2 h-2 rounded-full bg-emerald-400" />Balance</span>
            <span className="flex items-center gap-2 text-xs text-gray-400"><span className="w-2 h-2 rounded-full bg-red-400" />Claims Paid</span>
          </div>
        </div>

        {/* Treasury Details */}
        <div className="space-y-4">
          <div className="bg-[#0f1420] border border-white/5 rounded-xl p-6">
            <div className="grid grid-cols-2 gap-6">
              <div>
                <div className="text-xs text-gray-500 uppercase tracking-wider mb-1">Premium Pool</div>
                <div className="text-2xl font-bold text-emerald-400">{treasury.premium_pool} USDC</div>
              </div>
              <div>
                <div className="text-xs text-gray-500 uppercase tracking-wider mb-1">Claims Paid</div>
                <div className="text-2xl font-bold text-red-400">{treasury.claims_paid} USDC</div>
              </div>
              <div>
                <div className="text-xs text-gray-500 uppercase tracking-wider mb-1">Current Balance</div>
                <div className="text-2xl font-bold text-white">{treasury.current_balance} USDC</div>
              </div>
              <div>
                <div className="text-xs text-gray-500 uppercase tracking-wider mb-1">Profit Margin</div>
                <div className={`text-2xl font-bold ${treasury.profit >= 0 ? "text-emerald-400" : "text-red-400"}`}>
                  {treasury.profit_margin}%
                </div>
              </div>
            </div>
          </div>

          {wallet && (
            <div className="bg-[#0f1420] border border-cyan-500/10 rounded-xl p-6">
              <h3 className="text-sm font-semibold text-cyan-400 mb-3">🔗 GOAT Network Wallet</h3>
              <div className="space-y-2">
                <div className="flex justify-between text-sm">
                  <span className="text-gray-500">Address</span>
                  <span className="font-mono text-gray-300">{wallet.wallet?.slice(0, 10)}…{wallet.wallet?.slice(-8)}</span>
                </div>
                <div className="flex justify-between text-sm">
                  <span className="text-gray-500">Balance</span>
                  <span className="font-bold text-cyan-400">{wallet.balance_btc?.toFixed(8)} BTC</span>
                </div>
                <div className="flex justify-between text-sm">
                  <span className="text-gray-500">Status</span>
                  <span className={wallet.real_balance ? "text-emerald-400" : "text-gray-400"}>
                    {wallet.real_balance ? "🟢 Live" : "⚪ Simulated"}
                  </span>
                </div>
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
