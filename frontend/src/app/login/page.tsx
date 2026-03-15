"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";
import { Shield } from "lucide-react";

export default function LoginPage() {
  const router = useRouter();
  const [role, setRole] = useState<"farmer" | "gig_worker" | "admin">("farmer");
  const [wallet, setWallet] = useState("");

  const handleLogin = (e: React.FormEvent) => {
    e.preventDefault();
    localStorage.setItem("cs_role", role);
    localStorage.setItem("cs_wallet", wallet || "0xDemo");
    if (role === "admin") {
      router.push("/dashboard/admin");
    } else {
      router.push("/dashboard/user");
    }
  };

  return (
    <div className="min-h-screen flex items-center justify-center bg-[#060a13] px-4">
      <div className="w-full max-w-md">
        {/* Logo */}
        <div className="text-center mb-10">
          <div className="inline-flex items-center justify-center w-16 h-16 rounded-2xl bg-emerald-500/10 mb-4">
            <Shield className="w-8 h-8 text-emerald-400" />
          </div>
          <h1 className="text-2xl font-bold bg-gradient-to-r from-emerald-400 to-cyan-400 bg-clip-text text-transparent">
            Welcome to ClimaShield
          </h1>
          <p className="text-gray-500 mt-2 text-sm">
            AI Parametric Insurance • GOAT Network
          </p>
        </div>

        {/* Card */}
        <form
          onSubmit={handleLogin}
          className="bg-[#0f1420] border border-white/5 rounded-2xl p-8 space-y-6"
        >
          {/* Connect Wallet */}
          <div>
            <label className="text-xs font-medium uppercase tracking-wider text-gray-500 mb-2 block">
              Connect Your Wallet
            </label>
            <input
              type="text"
              placeholder="0x34817DDAAb4E..."
              value={wallet}
              onChange={(e) => setWallet(e.target.value)}
              className="w-full px-4 py-3 bg-[#0a0f1a] border border-white/10 rounded-xl text-sm text-white placeholder-gray-600 focus:border-emerald-500/50 focus:outline-none transition"
            />
          </div>

          {/* Select Persona */}
          <div>
            <label className="text-xs font-medium uppercase tracking-wider text-gray-500 mb-3 block">
              Select Your Persona
            </label>
            <div className="grid grid-cols-3 gap-3">
              {([
                { key: "farmer" as const, label: "Farmer", emoji: "🌾" },
                { key: "gig_worker" as const, label: "Gig Worker", emoji: "🛵" },
                { key: "admin" as const, label: "Admin", emoji: "🏢" },
              ]).map((p) => (
                <button
                  key={p.key}
                  type="button"
                  onClick={() => setRole(p.key)}
                  className={`flex flex-col items-center gap-2 p-4 rounded-xl border text-sm font-medium transition-all duration-200 ${
                    role === p.key
                      ? "bg-emerald-500/10 border-emerald-500/30 text-emerald-400"
                      : "bg-[#0a0f1a] border-white/5 text-gray-400 hover:border-white/10"
                  }`}
                >
                  <span className="text-2xl">{p.emoji}</span>
                  <span>{p.label}</span>
                </button>
              ))}
            </div>
          </div>

          {/* Submit */}
          <button
            type="submit"
            className="w-full py-3 rounded-xl bg-gradient-to-r from-emerald-500 to-cyan-500 text-white font-semibold text-sm hover:opacity-90 transition shadow-lg shadow-emerald-500/20"
          >
            Enter Dashboard →
          </button>
        </form>

        <p className="text-center text-gray-600 text-xs mt-6">
          Powered by GOAT Testnet3 • x402 Protocol
        </p>
      </div>
    </div>
  );
}
