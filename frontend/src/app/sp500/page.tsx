import {
  getSp500ScreenerResults
} from "@/lib/api";
import Sp500Dashboard from "@/components/Sp500Dashboard";
import Sidebar from "@/components/Sidebar";
import Link from "next/link";

export const revalidate = 300;

export default async function Sp500Page() {
  const sp500Data = await getSp500ScreenerResults();

  return (
    <main className="flex h-screen overflow-hidden bg-abyssal">
      {/* ===== NAV SIDEBAR ===== */}
      <Sidebar />

      {/* ===== MAIN CONTAINER ===== */}
      <div className="flex-1 flex flex-col min-w-0 overflow-hidden">
        {/* Topbar */}
        <header className="h-12 border-b border-panel-light/30 bg-abyssal flex items-center px-5 justify-between shrink-0">
          <div className="flex items-center space-x-2">
            <div className="w-2 h-2 rounded-full bg-[#FFD700] shadow-[0_0_8px_rgba(255,215,0,0.6)] animate-pulse"></div>
            <span className="text-[10px] font-mono text-muted-text uppercase tracking-wider">Fundamental Screener // S&P 500</span>
          </div>
          <div className="flex lg:hidden gap-2">
            <Link href="/" className="text-[10px] font-mono text-muted-text border border-panel-light px-2 py-1 rounded">Charts</Link>
            <Link href="/scanner" className="text-[10px] font-mono text-muted-text border border-panel-light px-2 py-1 rounded">Scanner</Link>
            <Link href="/sp500" className="text-[10px] font-mono text-accent border border-accent/30 px-2 py-1 rounded">S&P 500</Link>
          </div>
        </header>

        {/* S&P 500 Content - fills remaining space, no page scroll */}
        <div className="flex-1 overflow-hidden">
          <Sp500Dashboard sp500Data={sp500Data} />
        </div>
      </div>
    </main>
  );
}
