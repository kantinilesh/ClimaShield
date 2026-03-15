"use client";

import { useEffect, useState } from "react";
import { getTreasuryStatus } from "@/services/api";

export default function UserPayments() {
  const [treasury, setTreasury] = useState<any>(null);

  useEffect(() => {
    getTreasuryStatus().then(setTreasury).catch(() => {});
  }, []);

  return (
    <div className="space-y-6 animate-in">
      <h1 className="text-2xl font-bold">Premium Payments</h1>

      {treasury && (
        <div className="grid grid-cols-2 gap-4">
          <div className="bg-[#0f1420] border border-white/5 rounded-xl p-5">
            <div className="text-xs text-gray-500 uppercase mb-1">Total Premiums Paid</div>
            <div className="text-2xl font-bold text-cyan-400">{treasury.total_premiums || treasury.premium_pool || 0} USDC</div>
          </div>
          <div className="bg-[#0f1420] border border-white/5 rounded-xl p-5">
            <div className="text-xs text-gray-500 uppercase mb-1">Total Claims Received</div>
            <div className="text-2xl font-bold text-emerald-400">{treasury.total_payouts || treasury.claims_paid || 0} USDC</div>
          </div>
        </div>
      )}

      <div className="bg-[#0f1420] border border-white/5 rounded-xl p-8 text-center text-gray-500">
        <p>Payment history will appear here as you make premium payments via the Telegram bot.</p>
        <p className="text-xs mt-2 text-gray-600">Use <code className="text-emerald-400">/pay_premium CS1001</code> in the bot</p>
      </div>
    </div>
  );
}
