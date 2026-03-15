"use client";

import { useEffect, useState } from "react";
import { getOracleLatest } from "@/services/api";
import { Droplets, Thermometer, Wind, Eye } from "lucide-react";

export default function UserWeather() {
  const [data, setData] = useState<any>(null);

  useEffect(() => {
    const load = () => getOracleLatest().then(setData).catch(() => {});
    load();
    const id = setInterval(load, 30000);
    return () => clearInterval(id);
  }, []);

  return (
    <div className="space-y-6 animate-in">
      <div className="flex items-center justify-between">
        <h1 className="text-2xl font-bold">Weather Alerts</h1>
        <span className="flex items-center gap-2 text-xs text-gray-500">
          <span className="w-2 h-2 rounded-full bg-cyan-400 animate-pulse" />
          Live weather data
        </span>
      </div>

      <div className="grid grid-cols-2 lg:grid-cols-4 gap-4">
        <div className="bg-[#0f1420] border border-white/5 rounded-xl p-5 text-center">
          <Droplets className="w-8 h-8 text-cyan-400 mx-auto mb-2" />
          <div className="text-xs text-gray-500 mb-1">Rainfall</div>
          <div className="text-xl font-bold">Normal</div>
        </div>
        <div className="bg-[#0f1420] border border-white/5 rounded-xl p-5 text-center">
          <Thermometer className="w-8 h-8 text-amber-400 mx-auto mb-2" />
          <div className="text-xs text-gray-500 mb-1">Temperature</div>
          <div className="text-xl font-bold">Moderate</div>
        </div>
        <div className="bg-[#0f1420] border border-white/5 rounded-xl p-5 text-center">
          <Wind className="w-8 h-8 text-emerald-400 mx-auto mb-2" />
          <div className="text-xs text-gray-500 mb-1">Air Quality</div>
          <div className="text-xl font-bold">Good</div>
        </div>
        <div className="bg-[#0f1420] border border-white/5 rounded-xl p-5 text-center">
          <Eye className="w-8 h-8 text-purple-400 mx-auto mb-2" />
          <div className="text-xs text-gray-500 mb-1">Active Alerts</div>
          <div className="text-xl font-bold">{data?.total || 0}</div>
        </div>
      </div>

      {data?.events?.length > 0 && (
        <div className="bg-[#0f1420] border border-white/5 rounded-xl overflow-hidden">
          <div className="px-6 py-4 border-b border-white/5">
            <h3 className="text-sm font-semibold text-gray-300">Recent Oracle Events</h3>
          </div>
          <div className="overflow-x-auto">
            <table className="w-full">
              <thead>
                <tr className="border-b border-white/5">
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">City</th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Type</th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Value</th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Timestamp</th>
                </tr>
              </thead>
              <tbody>
                {data.events.map((e: any, i: number) => (
                  <tr key={i} className="border-b border-white/5 hover:bg-white/[0.02]">
                    <td className="px-6 py-3 text-sm">{e.city}</td>
                    <td className="px-6 py-3 text-sm capitalize">{e.type || e.category}</td>
                    <td className="px-6 py-3 text-sm font-mono">{e.value || "—"}</td>
                    <td className="px-6 py-3 text-sm text-gray-500">{e.timestamp ? new Date(e.timestamp).toLocaleString() : "—"}</td>
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
