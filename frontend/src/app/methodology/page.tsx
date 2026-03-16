import Sidebar from "@/components/Sidebar";

export default function MethodologyPage() {
  return (
    <main className="flex h-screen overflow-hidden bg-abyssal">
      <Sidebar />

      <div className="flex-1 flex flex-col min-w-0 overflow-hidden">
        {/* Topbar */}
        <header className="h-12 border-b border-panel-light/30 bg-abyssal flex items-center px-5 justify-between shrink-0">
          <div className="flex items-center space-x-2">
            <div className="w-2 h-2 rounded-full bg-accent shadow-[0_0_8px_rgba(0,194,255,0.6)] animate-pulse"></div>
            <span className="text-[10px] font-mono text-muted-text uppercase tracking-wider">Navigational Chart // Methodology</span>
          </div>
        </header>

        {/* Content Area */}
        <div className="flex-1 overflow-y-auto custom-scrollbar p-8">
          <div className="max-w-4xl mx-auto space-y-12 pb-20">
            
            {/* Header Section */}
            <section className="text-center space-y-4">
              <h1 className="text-4xl font-bold text-white tracking-tight">The <span className="text-accent underline decoration-accent/30 underline-offset-8">SwingFish</span> Methodology</h1>
              <p className="text-muted-text font-mono text-sm max-w-2xl mx-auto uppercase tracking-widest leading-relaxed">
                Strategic Intelligence for Deep Water Trading
              </p>
              <div className="h-1 w-24 bg-gradient-to-r from-transparent via-accent to-transparent mx-auto mt-6"></div>
            </section>

            {/* Pillar 1: Dashboard / Data Fetching */}
            <section className="bg-panel border border-panel-light/30 rounded-lg overflow-hidden">
              <div className="bg-panel-light/10 px-6 py-4 border-b border-panel-light/30 flex items-center gap-3">
                <span className="text-2xl">📡</span>
                <h2 className="text-lg font-bold text-white uppercase tracking-wider font-mono">Pillar I: Data Provider Engine</h2>
              </div>
              <div className="p-8 space-y-6">
                <p className="text-primary-text leading-relaxed">
                  Before any interpretation occurs, the **Dashboard** acts as our sonar, extracting institutional-grade "raw data" from reliable sources like Yahoo Finance, FRED, and ForexFactory.
                </p>
                <div className="grid md:grid-cols-3 gap-6">
                  <div className="bg-abyssal/50 p-4 rounded border border-panel-light/20">
                    <h3 className="text-accent font-bold text-xs uppercase mb-2 font-mono">Micro & Fundamentals</h3>
                    <p className="text-[11px] text-muted-text leading-relaxed">
                      Detailed x-rays of corporate health, including insider transactions and institutional holdings (Smart Money).
                    </p>
                  </div>
                  <div className="bg-abyssal/50 p-4 rounded border border-panel-light/20">
                    <h3 className="text-accent font-bold text-xs uppercase mb-2 font-mono">Macro & Flows</h3>
                    <p className="text-[11px] text-muted-text leading-relaxed">
                      Market regime analysis via COT (Commitment of Traders), FED data, and high-impact economic calendars.
                    </p>
                  </div>
                  <div className="bg-abyssal/50 p-4 rounded border border-panel-light/20">
                    <h3 className="text-accent font-bold text-xs uppercase mb-2 font-mono">Algorithmic Scanner</h3>
                    <p className="text-[11px] text-muted-text leading-relaxed">
                      Real-time identification of volatility and liquidity bursts across the entire market spectrum.
                    </p>
                  </div>
                </div>
              </div>
            </section>

            {/* Pillar 2: Multiagent Analysis */}
            <section className="bg-panel border border-panel-light/30 rounded-lg overflow-hidden">
              <div className="bg-panel-light/10 px-6 py-4 border-b border-panel-light/30 flex items-center gap-3">
                <span className="text-2xl">🔱</span>
                <h2 className="text-lg font-bold text-white uppercase tracking-wider font-mono">Pillar II: The Intelligence Committee</h2>
              </div>
              <div className="p-8 space-y-6">
                <p className="text-primary-text leading-relaxed">
                  The **Abyssal Probe** utilizes 6 specialized AI agents orchestrated by a complex graph to eliminate emotional bias and "hallucinations".
                </p>
                
                <div className="space-y-4">
                  {[
                    { name: "Technical Analyst", details: "Studies Ichimoku Clouds, RSI, and ATR for entry points and momentum." },
                    { name: "Risk Officer (CRO)", details: "Projecting 10,000 Monte Carlo scenarios to calculate VaR (Value at Risk)." },
                    { name: "Options Specialist", details: "Analyzes Put/Call skew and Expected Move dictated by the derivatives market." },
                    { name: "Fundamental specialist", details: "Scrutinizes P/E ratios and corporate valuation vs. analyst consensus." },
                    { name: "Sentiment & News", details: "NLP-driven evaluation of market narrative and news sentiment gaps." },
                    { name: "Macro Strategist", details: "Monitors credit spreads, bond yields (TNX), and institutional risk appetite." }
                  ].map((agent, i) => (
                    <div key={i} className="flex gap-4 items-start bg-abyssal/30 p-3 rounded border-l-2 border-accent">
                      <div className="text-[10px] font-mono text-accent font-bold uppercase w-32 shrink-0">{agent.name}</div>
                      <div className="text-xs text-muted-text">{agent.details}</div>
                    </div>
                  ))}
                </div>

                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                  <div className="mt-6 flex items-center gap-4 bg-accent/10 p-4 rounded border border-accent/20">
                    <div className="text-xl">🤵</div>
                    <div className="space-y-1">
                      <h3 className="text-xs font-bold text-white uppercase font-mono">The Portfolio Manager</h3>
                      <p className="text-[11px] text-muted-text">
                        A senior supervisor (GPT-4o) that cross-validates all reports to issue "The Verdict": LONG, SHORT, or CASH.
                      </p>
                    </div>
                  </div>
                  <div className="mt-6 flex items-center gap-4 bg-abyssal/80 p-4 rounded border border-panel-light/30">
                    <div className="text-xl">📄</div>
                    <div className="space-y-1">
                      <h3 className="text-xs font-bold text-white uppercase font-mono">Institutional Audit Trail</h3>
                      <p className="text-[11px] text-muted-text">
                        Every report generates a dual PDF: an Executive Summary and a "Deep-Dive" Audit Trail comparing raw data vs. AI reasoning.
                      </p>
                    </div>
                  </div>
                </div>
              </div>
            </section>

            {/* Pillar 3: S&P 500 Scoring */}
            <section className="bg-panel border border-panel-light/30 rounded-lg overflow-hidden">
              <div className="bg-panel-light/10 px-6 py-4 border-b border-panel-light/30 flex items-center gap-3">
                <span className="text-2xl">📈</span>
                <h2 className="text-lg font-bold text-white uppercase tracking-wider font-mono">Pillar III: The Scoring Engine</h2>
              </div>
              <div className="p-8 space-y-6">
                <p className="text-primary-text leading-relaxed">
                  For the S&P 500 universe, we utilize a mathematically rigorous scoring system (0-100) based on five proven financial models.
                </p>

                <div className="grid grid-cols-1 gap-3">
                  <div className="flex items-center justify-between p-3 bg-abyssal/50 rounded border border-panel-light/10">
                    <span className="text-xs font-mono text-white">Piotroski F-Score (15%)</span>
                    <span className="text-[10px] text-muted-text uppercase italic">Financial Strength</span>
                  </div>
                  <div className="flex items-center justify-between p-3 bg-abyssal/50 rounded border border-panel-light/10">
                    <span className="text-xs font-mono text-white">Altman Z-Score (10%)</span>
                    <span className="text-[10px] text-muted-text uppercase italic">Insolvency Risk</span>
                  </div>
                  <div className="flex items-center justify-between p-3 bg-abyssal/50 rounded border border-panel-light/10">
                    <span className="text-xs font-mono text-white">Beneish M-Score (5%)</span>
                    <span className="text-[10px] text-muted-text uppercase italic">Accounting Integrity</span>
                  </div>
                  <div className="flex items-center justify-between p-3 bg-abyssal/50 rounded border border-panel-light/10">
                    <span className="text-xs font-mono text-white">Magic Formula (20%)</span>
                    <span className="text-[10px] text-muted-text uppercase italic">Quality × Price</span>
                  </div>
                  <div className="flex items-center justify-between p-3 bg-abyssal/50 rounded border border-panel-light/20 border-accent/20">
                    <span className="text-xs font-mono text-accent font-bold">Growth & Momentum (30%)</span>
                    <span className="text-[10px] text-accent/70 uppercase font-bold">Trend Validation</span>
                  </div>
                  <div className="flex items-center justify-between p-3 bg-abyssal/50 rounded border border-panel-light/10">
                    <span className="text-xs font-mono text-white">Analyst Upside (20%)</span>
                    <span className="text-[10px] text-muted-text uppercase italic">Institutional Targets</span>
                  </div>
                </div>

                <div className="p-4 bg-abyssal rounded border border-panel-light/10">
                  <h4 className="text-[10px] font-bold text-muted-text uppercase mb-2">Verdict Logic:</h4>
                  <div className="flex gap-2">
                    <span className="px-2 py-0.5 rounded bg-success/20 text-success text-[10px] uppercase font-bold">Strong Buy (80+)</span>
                    <span className="px-2 py-0.5 rounded bg-amber-500/20 text-amber-500 text-[10px] uppercase font-bold">Hold (30-65)</span>
                    <span className="px-2 py-0.5 rounded bg-danger/20 text-danger text-[10px] uppercase font-bold">Sell (&lt;30)</span>
                  </div>
                </div>
              </div>
            </section>

          </div>
        </div>
      </div>
    </main>
  );
}
