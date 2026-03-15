"use client";

import { useEffect, useState } from "react";
import { getOracleEvents } from "@/services/api";

export default function AdminWeather() {
  const [data, setData] = useState<any>(null);

  useEffect(() => {
    const load = () => getOracleEvents().then(setData).catch(() => {});
    load();
    const id = setInterval(load, 30000);
    return () => clearInterval(id);
  }, []);

  return (
    <div className="space-y-6 animate-in">
      <div className="flex items-center justify-between">
        <h1 className="text-2xl font-bold">Oracle Monitor</h1>
        <span className="flex items-center gap-2 text-xs text-gray-500">
          <span className="w-2 h-2 rounded-full bg-amber-400 animate-pulse" />
          Weather data updates every 30s
        </span>
      </div>

      <div className="bg-[#0f1420] border border-white/5 rounded-xl overflow-hidden">
        <div className="overflow-x-auto">
          <table className="w-full">
            <thead>
              <tr className="border-b border-white/5">
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">City</th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Event Type</th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Value</th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Threshold</th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Triggered</th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Timestamp</th>
              </tr>
            </thead>
            <tbody>
              {(!data?.events || data.events.length === 0) && (
                <tr><td colSpan={6} className="px-6 py-8 text-center text-gray-500">No oracle events yet. Events appear when weather data is checked.</td></tr>
              )}
              {data?.events?.map((e: any, i: number) => (
                <tr key={i} className="border-b border-white/5 hover:bg-white/[0.02]">
                  <td className="px-6 py-3 text-sm font-medium">{e.city}</td>
                  <td className="px-6 py-3 text-sm capitalize">{e.event_type}</td>
                  <td className="px-6 py-3 text-sm font-mono">{e.value}</td>
                  <td className="px-6 py-3 text-sm font-mono text-gray-400">{e.threshold}</td>
                  <td className="px-6 py-3">
                    <span className={`px-2.5 py-0.5 rounded-full text-xs font-medium ${
                      e.exceeded ? "bg-red-500/10 text-red-400" : "bg-emerald-500/10 text-emerald-400"
                    }`}>{e.exceeded ? "⚠️ Yes" : "✅ No"}</span>
                  </td>
                  <td className="px-6 py-3 text-sm text-gray-500">{e.created_at ? new Date(e.created_at).toLocaleString() : "—"}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
}
