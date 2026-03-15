"use client";

import { useEffect, useState } from "react";
import { getAdminPolicies } from "@/services/api";

export default function AdminPolicies() {
  const [data, setData] = useState<any>(null);
  const [filter, setFilter] = useState<string>("");

  useEffect(() => {
    getAdminPolicies(filter || undefined).then(setData).catch(() => {});
  }, [filter]);

  return (
    <div className="space-y-6 animate-in">
      <div className="flex items-center justify-between">
        <h1 className="text-2xl font-bold">Policy Management</h1>
        <select
          value={filter}
          onChange={(e) => setFilter(e.target.value)}
          className="bg-[#0f1420] border border-white/10 rounded-lg px-3 py-2 text-sm text-gray-300 focus:outline-none focus:border-emerald-500/50"
        >
          <option value="">All Policies</option>
          <option value="active">Active</option>
          <option value="cancelled">Cancelled</option>
        </select>
      </div>

      <div className="bg-[#0f1420] border border-white/5 rounded-xl overflow-hidden">
        <div className="overflow-x-auto">
          <table className="w-full">
            <thead>
              <tr className="border-b border-white/5">
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Policy ID</th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">User Wallet</th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">City</th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Type</th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Premium</th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Coverage</th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Status</th>
              </tr>
            </thead>
            <tbody>
              {data?.policies?.map((p: any) => (
                <tr key={p.policy_id} className="border-b border-white/5 hover:bg-white/[0.02]">
                  <td className="px-6 py-3 text-sm font-mono text-emerald-400">{p.policy_id}</td>
                  <td className="px-6 py-3 text-sm text-gray-400 font-mono">{(p.user_wallet || "—").slice(0, 10)}…</td>
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
        {data && (
          <div className="px-6 py-3 border-t border-white/5 text-xs text-gray-500">
            {data.total} policies total
          </div>
        )}
      </div>
    </div>
  );
}
