"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";

export default function Sidebar() {
  const pathname = usePathname();

  const links = [
    { href: "/", label: "📊 Macro Charts" },
    { href: "/scanner", label: "🔍 Scanner & Intel" },
    { href: "/sp500", label: "📈 S&P 500 Screener" },
    { href: "/analysis", label: "🔱 Abyssal Probe" },
    { href: "/methodology", label: "📚 Marine Manual" },
  ];

  return (
    <aside className="w-52 border-r border-panel-light/30 bg-panel hidden lg:flex flex-col shrink-0">
      <div className="h-14 flex items-center px-5 border-b border-panel-light/30">
        <span className="font-bold text-lg tracking-tight text-primary-text">
          Swing<span className="text-accent">Fish</span>
        </span>
      </div>
      <nav className="flex-1 p-3 space-y-1">
        {links.map((link) => {
          const isActive = pathname === link.href;
          return (
            <Link
              key={link.href}
              href={link.href}
              className={`flex items-center gap-2 px-3 py-2 rounded text-xs font-mono transition-colors ${
                isActive
                  ? "bg-panel-light/20 border border-accent/30 text-accent"
                  : "text-muted-text hover:bg-panel-light/20 hover:text-primary-text"
              }`}
            >
              {link.label}
            </Link>
          );
        })}
      </nav>
      <div className="p-3 border-t border-panel-light/30">
        <div className="text-[9px] font-mono text-muted-text/40 uppercase">SwingFish v1.0</div>
      </div>
    </aside>
  );
}
