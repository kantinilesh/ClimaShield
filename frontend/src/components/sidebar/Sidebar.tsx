"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import { useState } from "react";
import {
  LayoutDashboard, FileText, AlertTriangle, Cloud,
  Landmark, ScrollText, Settings, ChevronLeft, Shield,
  LogOut, Menu,
} from "lucide-react";
import { clsx } from "clsx";

interface SidebarProps {
  role: "admin" | "user";
}

const adminNav = [
  { label: "Dashboard", href: "/dashboard/admin", icon: LayoutDashboard },
  { label: "Policies", href: "/dashboard/admin/policies", icon: FileText },
  { label: "Claims", href: "/dashboard/admin/claims", icon: AlertTriangle },
  { label: "Weather", href: "/dashboard/admin/weather", icon: Cloud },
  { label: "Treasury", href: "/dashboard/admin/treasury", icon: Landmark },
  { label: "Logs", href: "/dashboard/admin/logs", icon: ScrollText },
  { label: "Settings", href: "/dashboard/admin/settings", icon: Settings },
];

const userNav = [
  { label: "Dashboard", href: "/dashboard/user", icon: LayoutDashboard },
  { label: "My Policies", href: "/dashboard/user/policies", icon: FileText },
  { label: "Claims", href: "/dashboard/user/claims", icon: AlertTriangle },
  { label: "Weather", href: "/dashboard/user/weather", icon: Cloud },
  { label: "Payments", href: "/dashboard/user/payments", icon: Landmark },
  { label: "Settings", href: "/dashboard/user/settings", icon: Settings },
];

export default function Sidebar({ role }: SidebarProps) {
  const pathname = usePathname();
  const [collapsed, setCollapsed] = useState(false);
  const items = role === "admin" ? adminNav : userNav;

  return (
    <aside
      className={clsx(
        "fixed left-0 top-0 h-screen bg-[#0a0f1a] border-r border-white/5 flex flex-col z-50 transition-all duration-300",
        collapsed ? "w-[72px]" : "w-[250px]"
      )}
    >
      {/* Logo */}
      <div className="flex items-center gap-3 px-5 py-6 border-b border-white/5">
        <Shield className="w-8 h-8 text-emerald-400 shrink-0" />
        {!collapsed && (
          <span className="text-lg font-bold bg-gradient-to-r from-emerald-400 to-cyan-400 bg-clip-text text-transparent">
            ClimaShield
          </span>
        )}
      </div>

      {/* Nav Items */}
      <nav className="flex-1 py-4 px-3 space-y-1">
        {items.map((item) => {
          const active = pathname === item.href || pathname.startsWith(item.href + "/");
          const Icon = item.icon;
          return (
            <Link
              key={item.href}
              href={item.href}
              className={clsx(
                "flex items-center gap-3 px-3 py-2.5 rounded-lg text-sm font-medium transition-all duration-200",
                active
                  ? "bg-emerald-500/10 text-emerald-400 shadow-[inset_0_0_0_1px_rgba(52,211,153,0.15)]"
                  : "text-gray-400 hover:bg-white/5 hover:text-gray-200"
              )}
            >
              <Icon className="w-5 h-5 shrink-0" />
              {!collapsed && <span>{item.label}</span>}
            </Link>
          );
        })}
      </nav>

      {/* Footer */}
      <div className="p-3 border-t border-white/5 space-y-1">
        <button
          onClick={() => setCollapsed(!collapsed)}
          className="flex items-center gap-3 px-3 py-2.5 rounded-lg text-sm text-gray-400 hover:bg-white/5 w-full"
        >
          {collapsed ? <Menu className="w-5 h-5" /> : <ChevronLeft className="w-5 h-5" />}
          {!collapsed && <span>Collapse</span>}
        </button>
        <Link
          href="/login"
          className="flex items-center gap-3 px-3 py-2.5 rounded-lg text-sm text-gray-400 hover:bg-red-500/10 hover:text-red-400 w-full"
        >
          <LogOut className="w-5 h-5 shrink-0" />
          {!collapsed && <span>Logout</span>}
        </Link>
      </div>
    </aside>
  );
}
