"use client";

import { useEffect, useState } from "react";
import { getClaimsHistory } from "@/services/api";

export default function UserClaims() {
  const [data, setData] = useState<any>(null);

  useEffect(() => {
    getClaimsHistory().then(setData).catch(() => {});
  }, []);

  const allClaims = [
    ...(data?.claims || []),
    ...(data?.payouts || []),
    ...(data?.simulated_claims || []),
  ];

  return (
    <div className="space-y-6 animate-in">
      <h1 className="text-2xl font-bold">Claim History</h1>

      <div className="bg-[#0f1420] border border-white/5 rounded-xl overflow-hidden">
        <table className="w-full">
          <thead>
            <tr className="border-b border-white/5">
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Category</th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Message</th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Timestamp</th>
            </tr>
          </thead>
          <tbody>
            {allClaims.length === 0 && (
              <tr><td colSpan={3} className="px-6 py-8 text-center text-gray-500">No claims yet. Claims are triggered when weather thresholds are breached.</td></tr>
            )}
            {allClaims.map((c: any, i: number) => (
              <tr key={i} className="border-b border-white/5 hover:bg-white/[0.02]">
                <td className="px-6 py-3">
                  <span className="px-2.5 py-0.5 rounded-full text-xs font-medium bg-amber-500/10 text-amber-400">{c.category}</span>
                </td>
                <td className="px-6 py-3 text-sm text-gray-300">{c.message}</td>
                <td className="px-6 py-3 text-sm text-gray-500">{c.timestamp ? new Date(c.timestamp).toLocaleString() : "—"}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}
