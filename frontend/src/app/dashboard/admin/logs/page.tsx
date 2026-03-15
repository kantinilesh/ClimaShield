"use client";

import { useEffect, useState } from "react";
import { getRecentLogs, getLogsSummary } from "@/services/api";

export default function AdminLogs() {
  const [logs, setLogs] = useState<any>(null);
  const [summary, setSummary] = useState<any>(null);

  useEffect(() => {
    const load = async () => {
      const [l, s] = await Promise.all([
        getRecentLogs(50).catch(() => null),
        getLogsSummary().catch(() => null),
      ]);
      setLogs(l);
      setSummary(s);
    };
    load();
    const id = setInterval(load, 10000);
    return () => clearInterval(id);
  }, []);

  const categoryColors: Record<string, string> = {
    policy_create: "text-emerald-400",
    premium_payment: "text-cyan-400",
    claim_payout: "text-red-400",
    auto_claim: "text-amber-400",
    oracle_check: "text-purple-400",
    simulation_claim: "text-pink-400",
    system: "text-gray-400",
  };

  return (
    <div className="space-y-6 animate-in">
      <div className="flex items-center justify-between">
        <h1 className="text-2xl font-bold">System Logs</h1>
        <span className="flex items-center gap-2 text-xs text-gray-500">
          <span className="w-2 h-2 rounded-full bg-emerald-400 animate-pulse" />
          Live • Refreshing every 10s
        </span>
      </div>

      {/* Summary chips */}
      {summary && (
        <div className="flex flex-wrap gap-2">
          {Object.entries(summary).map(([cat, count]) => (
            <span key={cat} className="px-3 py-1.5 bg-[#0f1420] border border-white/5 rounded-lg text-xs">
              <span className={categoryColors[cat] || "text-gray-400"}>{cat}</span>
              <span className="text-gray-500 ml-1.5">{String(count)}</span>
            </span>
          ))}
        </div>
      )}

      {/* Log entries */}
      <div className="bg-[#0f1420] border border-white/5 rounded-xl overflow-hidden">
        <div className="max-h-[600px] overflow-y-auto">
          {logs?.events?.map((e: any, i: number) => (
            <div key={i} className="flex items-start gap-4 px-6 py-3 border-b border-white/5 hover:bg-white/[0.02]">
              <span className="text-xs text-gray-600 font-mono mt-0.5 shrink-0 w-[140px]">
                {e.timestamp ? new Date(e.timestamp).toLocaleString() : "—"}
              </span>
              <span className={`text-xs font-medium uppercase shrink-0 w-[130px] ${categoryColors[e.category] || "text-gray-400"}`}>
                {e.category}
              </span>
              <span className="text-sm text-gray-300 flex-1">{e.message}</span>
            </div>
          ))}
          {(!logs?.events || logs.events.length === 0) && (
            <div className="px-6 py-8 text-center text-gray-500">No logs yet</div>
          )}
        </div>
      </div>
    </div>
  );
}
