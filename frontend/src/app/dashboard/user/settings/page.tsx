"use client";

export default function UserSettings() {
  return (
    <div className="space-y-6 animate-in">
      <h1 className="text-2xl font-bold">Settings</h1>
      <div className="bg-[#0f1420] border border-white/5 rounded-xl p-6 space-y-4">
        <h3 className="text-sm font-semibold text-gray-300">Account</h3>
        <div className="grid grid-cols-2 gap-4 text-sm">
          <div className="flex justify-between p-3 bg-[#0a0f1a] rounded-lg">
            <span className="text-gray-500">Wallet</span>
            <span className="font-mono text-gray-300">{typeof window !== "undefined" ? localStorage.getItem("cs_wallet") || "Not connected" : ""}</span>
          </div>
          <div className="flex justify-between p-3 bg-[#0a0f1a] rounded-lg">
            <span className="text-gray-500">Role</span>
            <span className="text-emerald-400 capitalize">{typeof window !== "undefined" ? localStorage.getItem("cs_role") || "user" : ""}</span>
          </div>
          <div className="flex justify-between p-3 bg-[#0a0f1a] rounded-lg">
            <span className="text-gray-500">Network</span>
            <span className="text-gray-300">GOAT Testnet3</span>
          </div>
          <div className="flex justify-between p-3 bg-[#0a0f1a] rounded-lg">
            <span className="text-gray-500">Version</span>
            <span className="text-gray-300">v0.5.0</span>
          </div>
        </div>
      </div>
    </div>
  );
}
