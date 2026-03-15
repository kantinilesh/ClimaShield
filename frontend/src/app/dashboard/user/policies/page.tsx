"use client";

import { useEffect, useState } from "react";
import { getPolicies } from "@/services/api";

export default function UserPolicies() {
  const [policies, setPolicies] = useState<any[]>([]);

  useEffect(() => {
    getPolicies().then((d) => setPolicies(d.policies || [])).catch(() => {});
  }, []);

  return (
    <div className="space-y-6 animate-in">
      <h1 className="text-2xl font-bold">My Policies</h1>

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
        {policies.map((p: any) => (
          <div key={p.policy_id} className="bg-[#0f1420] border border-white/5 rounded-xl p-5 hover:border-emerald-500/20 transition-all">
            <div className="flex items-center justify-between mb-3">
              <span className="font-mono text-emerald-400 text-sm font-bold">{p.policy_id}</span>
              <span className={`px-2.5 py-0.5 rounded-full text-xs font-medium ${
                p.status === "active" ? "bg-emerald-500/10 text-emerald-400" : "bg-red-500/10 text-red-400"
              }`}>{p.status}</span>
            </div>
            <div className="space-y-2 text-sm">
              <div className="flex justify-between"><span className="text-gray-500">City</span><span>{p.location}</span></div>
              <div className="flex justify-between"><span className="text-gray-500">Coverage</span><span className="capitalize">{p.coverage_type}</span></div>
              <div className="flex justify-between"><span className="text-gray-500">Threshold</span><span>{p.trigger_threshold}</span></div>
              <div className="flex justify-between"><span className="text-gray-500">Premium</span><span className="text-cyan-400">{p.premium_weekly} USDC/wk</span></div>
              <div className="flex justify-between"><span className="text-gray-500">Coverage Amt</span><span className="text-emerald-400">{p.coverage_amount} USDC</span></div>
            </div>
          </div>
        ))}
      </div>

      {policies.length === 0 && (
        <div className="text-center text-gray-500 py-12">No policies found. Create one through the Telegram bot!</div>
      )}
    </div>
  );
}
