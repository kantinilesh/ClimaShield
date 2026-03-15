import { clsx } from "clsx";
import { LucideIcon } from "lucide-react";

interface MetricCardProps {
  label: string;
  value: string | number;
  sub?: string;
  icon?: LucideIcon;
  trend?: "up" | "down" | "neutral";
  color?: "emerald" | "red" | "amber" | "cyan" | "white";
}

const colorMap = {
  emerald: "text-emerald-400",
  red: "text-red-400",
  amber: "text-amber-400",
  cyan: "text-cyan-400",
  white: "text-white",
};

const bgMap = {
  emerald: "bg-emerald-500/10",
  red: "bg-red-500/10",
  amber: "bg-amber-500/10",
  cyan: "bg-cyan-500/10",
  white: "bg-white/5",
};

export default function MetricCard({ label, value, sub, icon: Icon, color = "emerald" }: MetricCardProps) {
  return (
    <div className="bg-[#0f1420] border border-white/5 rounded-xl p-5 hover:border-emerald-500/20 transition-all duration-300 hover:shadow-[0_0_30px_rgba(52,211,153,0.04)]">
      <div className="flex items-start justify-between mb-3">
        <span className="text-xs font-medium uppercase tracking-wider text-gray-500">
          {label}
        </span>
        {Icon && (
          <div className={clsx("p-2 rounded-lg", bgMap[color])}>
            <Icon className={clsx("w-4 h-4", colorMap[color])} />
          </div>
        )}
      </div>
      <div className={clsx("text-2xl font-bold", colorMap[color])}>{value}</div>
      {sub && <div className="text-xs text-gray-500 mt-1">{sub}</div>}
    </div>
  );
}
