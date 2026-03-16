"use client";

import { useState } from "react";
import ReactMarkdown from "react-markdown";
import TabsContainer from "./TabsContainer";
import { runMultiagentAnalysis } from "@/lib/api";

type AnalysisResult = {
  ticker: string;
  decision: {
    executive_summary: string;
  };
  report_pdf_url: string;
  audit_pdf_url: string;
  technical_analysis?: string;
  fundamental_analysis?: string;
  macro_analysis?: string;
  sentiment_analysis?: string;
  options_analysis?: string;
  risk_analysis?: string;
};

export default function AbyssalProbe() {
  const [ticker, setTicker] = useState("");
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState<AnalysisResult | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [depth, setDepth] = useState(0);
  const [language, setLanguage] = useState("en");

  const baseUrl = (process.env.NEXT_PUBLIC_API_URL || 'http://127.0.0.1:8000').split('/api')[0];

  const startProbe = async () => {
    if (!ticker.trim()) return;
    setLoading(true);
    setError(null);
    setResult(null);
    setDepth(0);

    // Simulation of descent depth
    const depthInterval = setInterval(() => {
      setDepth((prev) => (prev < 10935 ? prev + Math.floor(Math.random() * 500) : 10935));
    }, 400);

    try {
      const data = await runMultiagentAnalysis(ticker.trim().toUpperCase(), language);
      if (!data) throw new Error("No intelligence recovered from the depths.");
      setResult(data);
    } catch (e: any) {
      setError(e.message);
    } finally {
      clearInterval(depthInterval);
      setLoading(false);
      setDepth(10935);
    }
  };

  const renderReport = (content: string | undefined) => (
    <div className="p-6 font-sans text-sm leading-relaxed text-primary-text bg-abyssal/50 rounded border border-panel-light/20 max-h-[600px] overflow-y-auto custom-scrollbar prose prose-invert prose-blue max-w-none">
      {content ? (
        <ReactMarkdown>{content}</ReactMarkdown>
      ) : (
        <span className="font-mono text-xs opacity-50">No data available for this sector.</span>
      )}
    </div>
  );

  const agents = [
    { 
      id: "verdict", 
      name: "Mission Commander", 
      role: "Strategic Decision", 
      icon: "🔱", 
      color: "text-accent",
      content: result?.decision.executive_summary 
    },
    { 
      id: "tech", 
      name: "T-800 Technical", 
      role: "Price & Chart Recon", 
      icon: "📐", 
      color: "text-blue-400",
      content: result?.technical_analysis 
    },
    { 
      id: "fund", 
      name: "Deep Core Fund", 
      role: "Equity & Value Analaysis", 
      icon: "🏢", 
      color: "text-green-400",
      content: result?.fundamental_analysis 
    },
    { 
      id: "macro", 
      name: "Global Current", 
      role: "Macroeconomic Flow", 
      icon: "🌍", 
      color: "text-purple-400",
      content: result?.macro_analysis 
    },
    { 
      id: "risk", 
      name: "Safe Harbor", 
      role: "Constraint & Risk Audit", 
      icon: "⚖️", 
      color: "text-danger",
      content: result?.risk_analysis 
    },
    { 
      id: "sent", 
      name: "Echo Locator", 
      role: "Social & News Sentiment", 
      icon: "🧠", 
      color: "text-amber-400",
      content: result?.sentiment_analysis 
    },
    { 
      id: "opt", 
      name: "Volatility Diver", 
      role: "Options & Gamma Recon", 
      icon: "🎲", 
      color: "text-indigo-400",
      content: result?.options_analysis 
    },
  ];

  const [activeAgentId, setActiveAgentId] = useState("verdict");
  const activeAgent = agents.find(a => a.id === activeAgentId) || agents[0];

  return (
    <div className="h-full flex flex-col space-y-6">
      {/* Search HUD */}
      <div className="bg-panel border border-panel-light/30 rounded-lg p-6 shadow-xl relative overflow-hidden">
        <div className="absolute top-0 right-0 w-64 h-64 bg-accent/5 rounded-full blur-3xl -mr-32 -mt-32"></div>
        
        <div className="relative z-10">
          <h2 className="text-xs uppercase tracking-[0.2em] text-accent font-bold mb-4 flex items-center gap-3">
            <span className="relative flex h-2 w-2">
              <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-accent opacity-75"></span>
              <span className="relative inline-flex rounded-full h-2 w-2 bg-accent"></span>
            </span>
            Deep Sea Speculation // Multiagent Probe
          </h2>

          <div className="flex gap-3">
            <div className="flex bg-abyssal border border-panel-light/50 rounded p-1 gap-1 min-w-fit">
              {[
                { code: "en", label: "EN", flag: "🇺🇸" },
                { code: "es", label: "ES", flag: "🇪🇸" },
                { code: "pt", label: "PT", flag: "🇧🇷" },
                { code: "zh", label: "ZH", flag: "🇨🇳" }
              ].map((lang) => (
                <button
                  key={lang.code}
                  onClick={() => setLanguage(lang.code)}
                  className={`flex flex-col items-center justify-center w-10 h-10 rounded transition-all border ${
                    language === lang.code 
                      ? "bg-accent/20 border-accent text-accent" 
                      : "border-transparent text-muted-text/50 hover:text-muted-text hover:bg-panel-light/10"
                  }`}
                >
                  <span className="text-xs scale-90">{lang.flag}</span>
                  <span className="text-[8px] font-bold font-mono">{lang.label}</span>
                </button>
              ))}
            </div>

            <div className="relative flex-1">
              <div className="absolute inset-y-0 left-0 pl-4 flex items-center pointer-events-none">
                <span className="text-muted-text/50 font-mono text-xs">TICKER_</span>
              </div>
              <input
                type="text"
                value={ticker}
                onChange={(e) => setTicker(e.target.value.toUpperCase())}
                onKeyDown={(e) => e.key === "Enter" && startProbe()}
                placeholder="AAPL, TSLA, BTC-USD..."
                disabled={loading}
                className="w-full bg-abyssal border border-panel-light/50 text-accent font-mono text-sm pl-20 pr-4 py-3 focus:outline-none focus:border-accent transition-all uppercase placeholder:text-muted-text/20 rounded"
              />
            </div>
            <button
              onClick={startProbe}
              disabled={loading || !ticker}
              className={`px-8 py-3 rounded font-mono text-xs font-bold uppercase tracking-widest transition-all ${
                loading 
                ? "bg-panel-light text-muted-text cursor-not-allowed" 
                : "bg-accent text-abyssal hover:bg-white hover:shadow-[0_0_20px_rgba(0,194,255,0.4)]"
              }`}
            >
              {loading ? "Descending..." : "Launch Probe"}
            </button>
          </div>
        </div>
      </div>

      {/* Main Display Area */}
      <div className="flex-1 min-h-0 bg-panel border border-panel-light/30 rounded-lg relative flex flex-col overflow-hidden">
        {loading ? (
          <div className="absolute inset-0 z-50 flex flex-col items-center justify-center bg-abyssal/80 backdrop-blur-sm">
            <div className="relative w-48 h-48 mb-8">
              {/* Sonar circles */}
              <div className="absolute inset-0 border-2 border-accent/20 rounded-full animate-[ping_3s_linear_infinite]"></div>
              <div className="absolute inset-0 border-2 border-accent/40 rounded-full animate-[ping_2s_linear_infinite]"></div>
              <div className="absolute inset-2 border border-accent/10 rounded-full"></div>
              
              {/* Depth reading */}
              <div className="absolute inset-0 flex flex-col items-center justify-center">
                <div className="text-[10px] text-accent uppercase font-mono tracking-tighter opacity-50 mb-1">Current Depth</div>
                <div className="text-2xl font-mono font-bold text-white tracking-widest">{depth}m</div>
                <div className="text-[8px] text-muted-text font-mono mt-2 animate-pulse">Scanning the Abyssal Zone...</div>
              </div>

              {/* Radar sweep */}
              <div className="absolute inset-0 border-r-2 border-accent/60 rounded-full animate-spin"></div>
            </div>
            
            <div className="flex flex-col gap-2 w-64">
                <div className="flex justify-between text-[10px] font-mono text-muted-text uppercase">
                    <span>Deploying Agents</span>
                    <span>100%</span>
                </div>
                <div className="h-1 bg-panel-light rounded-full overflow-hidden">
                    <div className="h-full bg-accent animate-[progress_20s_ease-in-out]"></div>
                </div>
            </div>
          </div>
        ) : result ? (
          <div className="h-full flex flex-col overflow-hidden">
            {/* Treasure Recovery Bar */}
            <div className="bg-gradient-to-r from-abyssal via-panel to-abyssal border-b border-panel-light/10 p-4 flex items-center justify-between shrink-0">
                <div className="flex items-center gap-3">
                    <div className="w-8 h-8 flex items-center justify-center rounded-full bg-[#FFD700]/10 border border-[#FFD700]/30 animate-pulse">
                        <span className="text-lg">💎</span>
                    </div>
                    <div>
                        <div className="text-[10px] uppercase tracking-tighter text-muted-text">Mission Status: </div>
                        <div className="text-[11px] font-bold text-accent uppercase tracking-widest">Treasures Recovered // {result.ticker}</div>
                    </div>
                </div>

                <div className="flex gap-4">
                    <a 
                        href={`${baseUrl}${result.report_pdf_url}`}
                        target="_blank"
                        className="treasure-btn flex items-center gap-2 px-4 py-2 rounded border border-[#FFD700]/10 bg-[#FFD700]/5 text-[#FFD700] transition-all overflow-hidden relative group"
                    >
                        <span className="text-xs">📂</span>
                        <span className="text-[10px] font-bold uppercase tracking-widest">Mission_Report.pdf</span>
                    </a>
                    <a 
                        href={`${baseUrl}${result.audit_pdf_url}`}
                        target="_blank"
                        className="treasure-btn flex items-center gap-2 px-4 py-2 rounded border-white/10 bg-white/5 text-white/70 hover:text-white transition-all overflow-hidden relative"
                    >
                        <span className="text-xs">🛡️</span>
                        <span className="text-[10px] font-bold uppercase tracking-widest">Audit_Trail.pdf</span>
                    </a>
                </div>
            </div>

            <div className="flex-1 flex min-h-0">
                {/* Agent Org Sidebar (Crew List) */}
                <div className="w-64 border-r border-panel-light/20 bg-abyssal/30 flex flex-col p-4 gap-4 overflow-y-auto custom-scrollbar">
                    <div className="text-[10px] font-bold text-muted-text uppercase tracking-widest mb-2 px-2">Crew Members</div>
                    
                    {/* Mission Commander (Special Styling) */}
                    <button 
                        onClick={() => setActiveAgentId("verdict")}
                        className={`text-left p-3 rounded-md border transition-all relative overflow-hidden group ${
                            activeAgentId === "verdict" 
                            ? "bg-accent/10 border-accent shadow-[0_0_15px_rgba(0,194,255,0.1)]" 
                            : "bg-panel/50 border-panel-light/30 hover:border-accent/50"
                        }`}
                    >
                        <div className="flex items-center gap-3 relative z-10">
                            <span className="text-xl">🔱</span>
                            <div>
                                <div className={`text-[11px] font-bold uppercase tracking-wide ${activeAgentId === "verdict" ? "text-accent" : "text-primary-text"}`}>Commander</div>
                                <div className="text-[9px] text-muted-text uppercase">Final Verdict</div>
                            </div>
                        </div>
                        {activeAgentId === "verdict" && (
                            <div className="absolute top-0 right-0 w-1 h-full bg-accent"></div>
                        )}
                    </button>

                    <div className="h-px bg-panel-light/20 my-2"></div>

                    {/* Specialists Grid/List */}
                    <div className="space-y-2">
                        {agents.slice(1).map(agent => (
                            <button 
                                key={agent.id}
                                onClick={() => setActiveAgentId(agent.id)}
                                className={`w-full text-left p-2.5 rounded border transition-all relative ${
                                    activeAgentId === agent.id 
                                    ? "bg-panel border-panel-light shadow-inner" 
                                    : "bg-transparent border-transparent hover:bg-panel-light/10"
                                }`}
                            >
                                <div className="flex items-center gap-3">
                                    <div className={`w-7 h-7 rounded flex items-center justify-center border ${
                                        activeAgentId === agent.id ? "bg-abyssal border-panel-light" : "bg-panel/40 border-panel-light/20"
                                    }`}>
                                        <span className="text-sm">{agent.icon}</span>
                                    </div>
                                    <div className="min-w-0">
                                        <div className={`text-[10px] font-bold uppercase truncate ${activeAgentId === agent.id ? "text-primary-text" : "text-muted-text"}`}>
                                            {agent.id.toUpperCase()} AGENT
                                        </div>
                                        <div className="text-[8px] text-muted-text/60 uppercase truncate">{agent.name}</div>
                                    </div>
                                </div>
                                {activeAgentId === agent.id && (
                                    <div className="absolute top-1/2 -right-1 w-2 h-2 bg-accent rounded-full -translate-y-1/2 blur-[2px]"></div>
                                )}
                            </button>
                        ))}
                    </div>
                </div>

                {/* Main Intel Display Area */}
                <div className="flex-1 flex flex-col min-w-0 bg-abyssal/10 relative">
                    {/* Header with Agent Info */}
                    <div className="p-6 border-b border-panel-light/10 bg-panel/20">
                        <div className="flex items-start justify-between">
                            <div>
                                <div className="flex items-center gap-2 mb-1">
                                    <span className="text-2xl">{activeAgent.icon}</span>
                                    <h2 className="text-lg font-bold text-primary-text tracking-tight">{activeAgent.name}</h2>
                                </div>
                                <div className="flex items-center gap-2">
                                    <span className={`text-[10px] font-bold uppercase tracking-[0.2em] px-2 py-0.5 rounded bg-abyssal border border-panel-light/50 ${activeAgent.color}`}>
                                        {activeAgent.role}
                                    </span>
                                    <span className="text-[10px] text-muted-text font-mono">STATUS: INTEL_RECOVERED</span>
                                </div>
                            </div>
                            <div className="text-right flex flex-col items-end opacity-40">
                                <div className="text-[10px] font-mono text-muted-text">SECTOR_ID: {activeAgent.id.toUpperCase()}</div>
                                <div className="text-[10px] font-mono text-muted-text">TIMESTAMP: {new Date().toLocaleTimeString()}</div>
                            </div>
                        </div>
                    </div>

                    {/* Content Display */}
                    <div className="flex-1 overflow-y-auto p-8 custom-scrollbar">
                        <div className="max-w-4xl mx-auto">
                            <div className="prose prose-invert prose-blue max-w-none font-sans text-sm leading-relaxed">
                                {activeAgent.content ? (
                                    <ReactMarkdown>{activeAgent.content}</ReactMarkdown>
                                ) : (
                                    <div className="flex flex-col items-center justify-center py-20 opacity-30">
                                        <div className="text-4xl mb-4 animate-pulse">📡</div>
                                        <div className="text-[10px] uppercase font-mono tracking-widest text-muted-text">Signals Lost in the Trench...</div>
                                    </div>
                                )}
                            </div>
                        </div>
                    </div>

                    {/* Faint Grid Overlay for Tactical Feel */}
                    <div className="absolute inset-0 pointer-events-none opacity-[0.02] bg-[radial-gradient(#00C2FF_1px,transparent_1px)] [background-size:20px_20px]"></div>
                </div>
            </div>
          </div>
        ) : error ? (
          <div className="flex flex-col items-center justify-center h-full text-center p-10">
            <div className="text-4xl mb-4">⚓</div>
            <h3 className="text-danger font-mono text-sm uppercase mb-2">Probe Failure</h3>
            <p className="text-muted-text font-mono text-xs max-w-md">{error}</p>
            <button onClick={() => setError(null)} className="mt-6 text-accent font-mono text-[10px] uppercase border-b border-accent/50 hover:border-accent">Dismiss Alert</button>
          </div>
        ) : (
          <div className="flex flex-col items-center justify-center h-full text-center p-10 opacity-30 grayscale pointer-events-none">
            <div className="text-6xl mb-6">🐋</div>
            <h3 className="text-primary-text font-mono text-sm uppercase tracking-[0.3em]">Ready for Descent</h3>
            <p className="text-muted-text font-mono text-[10px] mt-2">AWAITING TARGET COORDINATES FOR DEEP INTEL RECOVERY</p>
          </div>
        )}
      </div>

      <style jsx>{`
        @keyframes progress {
          0% { width: 0%; }
          10% { width: 10%; }
          30% { width: 45%; }
          70% { width: 85%; }
          100% { width: 95%; }
        }
        
        @keyframes shine {
          0% { left: -100%; }
          100% { left: 100%; }
        }

        .treasure-btn {
          background: linear-gradient(135deg, rgba(255, 215, 0, 0.1) 0%, rgba(255, 215, 0, 0.05) 100%);
          box-shadow: 0 0 10px rgba(255, 215, 0, 0.1);
        }

        .treasure-btn::before {
          content: "";
          position: absolute;
          top: 0;
          left: -100%;
          width: 100%;
          height: 100%;
          background: linear-gradient(
            to right,
            transparent,
            rgba(255, 215, 0, 0.2),
            transparent
          );
          transform: skewX(-30deg);
          animation: shine 4s infinite;
        }

        .treasure-btn:hover {
          background: linear-gradient(135deg, rgba(255, 215, 0, 0.2) 0%, rgba(255, 215, 0, 0.1) 100%);
          box-shadow: 0 0 20px rgba(255, 215, 0, 0.3), inset 0 0 10px rgba(255, 215, 0, 0.2);
          border-color: rgba(255, 215, 0, 0.6);
          transform: translateY(-1px);
        }

        .treasure-btn:active {
          transform: translateY(0);
        }

        .custom-scrollbar::-webkit-scrollbar {
          width: 4px;
        }
        .custom-scrollbar::-webkit-scrollbar-track {
          background: rgba(0,0,0,0);
        }
        .custom-scrollbar::-webkit-scrollbar-thumb {
          background: #172A3A;
          border-radius: 10px;
        }
      `}</style>
    </div>
  );
}
