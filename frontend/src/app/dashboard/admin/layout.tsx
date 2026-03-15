"use client";

import Sidebar from "@/components/sidebar/Sidebar";

export default function AdminLayout({ children }: { children: React.ReactNode }) {
  return (
    <div className="flex min-h-screen bg-[#060a13]">
      <Sidebar role="admin" />
      <main className="flex-1 ml-[250px] p-8 max-w-[1440px]">
        {children}
      </main>
    </div>
  );
}
