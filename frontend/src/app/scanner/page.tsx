import {
  getMarketScanner,
  getEconomicCalendar,
} from "@/lib/api";
import ScannerDashboard from "@/components/ScannerDashboard";
import Sidebar from "@/components/Sidebar";
import Link from "next/link";

export const revalidate = 300;

export default async function ScannerPage() {
  const [scannerData, calendarData] = await Promise.all([
    getMarketScanner(),
    getEconomicCalendar(),
  ]);

  return (
    <main className="flex h-screen overflow-hidden bg-abyssal">
      {/* ===== NAV SIDEBAR ===== */}
      <Sidebar />

      {/* ===== MAIN CONTAINER ===== */}
      <div className="flex-1 flex flex-col min-w-0 overflow-hidden">
        {/* Topbar */}
        <header className="h-12 border-b border-panel-light/30 bg-abyssal flex items-center px-5 justify-between shrink-0">
          <div className="flex items-center space-x-2">
            <div className="w-2 h-2 rounded-full bg-accent shadow-[0_0_8px_rgba(0,194,255,0.6)] animate-pulse"></div>
            <span className="text-[10px] font-mono text-muted-text uppercase tracking-wider">Scanner & Intelligence</span>
          </div>
          <div className="flex lg:hidden gap-2">
            <Link href="/" className="text-[10px] font-mono text-muted-text border border-panel-light px-2 py-1 rounded">Charts</Link>
            <Link href="/scanner" className="text-[10px] font-mono text-accent border border-accent/30 px-2 py-1 rounded">Scanner</Link>
            <Link href="/sp500" className="text-[10px] font-mono text-muted-text border border-panel-light px-2 py-1 rounded">S&P 500</Link>
          </div>
        </header>

        {/* Scanner Content - fills remaining space, no page scroll */}
        <div className="flex-1 overflow-hidden">
          <ScannerDashboard scannerData={scannerData} calendarData={calendarData} />
        </div>
      </div>
    </main>
  );
}
