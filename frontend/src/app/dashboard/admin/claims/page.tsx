"use client";

import { useEffect, useState } from "react";
import { getAdminClaims } from "@/services/api";

export default function AdminClaims() {
  const [data, setData] = useState<any>(null);

  useEffect(() => {
    getAdminClaims().then(setData).catch(() => {});
  }, []);

  return (
    <div className="space-y-6 animate-in">
      <h1 className="text-2xl font-bold">Claim Management</h1>

      <div className="bg-[#0f1420] border border-white/5 rounded-xl overflow-hidden">
        <div className="overflow-x-auto">
          <table className="w-full">
            <thead>
              <tr className="border-b border-white/5">
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Claim ID</th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Policy</th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Trigger Event</th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Payout</th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Tx Hash</th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Status</th>
              </tr>
            </thead>
            <tbody>
              {data?.claims?.length === 0 && (
                <tr><td colSpan={6} className="px-6 py-8 text-center text-gray-500">No claims yet. Claims appear when weather triggers are fired.</td></tr>
              )}
              {data?.claims?.map((c: any) => (
                <tr key={c.claim_id} className="border-b border-white/5 hover:bg-white/[0.02]">
                  <td className="px-6 py-3 text-sm font-mono text-amber-400">{c.claim_id}</td>
                  <td className="px-6 py-3 text-sm">{c.policy_id}</td>
                  <td className="px-6 py-3 text-sm text-gray-400 max-w-[200px] truncate">{c.trigger_event || "—"}</td>
                  <td className="px-6 py-3 text-sm text-red-400">{c.payout_amount} USDC</td>
                  <td className="px-6 py-3 text-sm font-mono text-gray-500">{c.tx_hash ? `${c.tx_hash.slice(0, 10)}…` : "—"}</td>
                  <td className="px-6 py-3">
                    <span className={`px-2.5 py-0.5 rounded-full text-xs font-medium ${
                      c.status === "paid" ? "bg-emerald-500/10 text-emerald-400" :
                      c.status === "verified" ? "bg-cyan-500/10 text-cyan-400" :
                      c.status === "rejected" ? "bg-red-500/10 text-red-400" :
                      "bg-amber-500/10 text-amber-400"
                    }`}>{c.status}</span>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
        {data && (
          <div className="px-6 py-3 border-t border-white/5 text-xs text-gray-500">
            {data.total} claims total
          </div>
        )}
      </div>
    </div>
  );
}
