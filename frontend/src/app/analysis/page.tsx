import Sidebar from "@/components/Sidebar";
import AbyssalProbe from "@/components/AbyssalProbe";

export default function AnalysisPage() {
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
            <span className="text-[10px] font-mono text-muted-text uppercase tracking-wider">
              Abyssal Probe // Deep Intelligence
            </span>
          </div>
        </header>

        {/* Content */}
        <div className="flex-1 overflow-hidden p-6">
          <AbyssalProbe />
        </div>
      </div>
    </main>
  );
}
