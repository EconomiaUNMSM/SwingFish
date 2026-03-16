"use client";

import TabsContainer from "./TabsContainer";
import { useState } from "react";
import { runSp500Screener } from "@/lib/api";

interface Props {
  sp500Data: any;
}

export default function Sp500Dashboard({ sp500Data }: Props) {
  const [searchTerm, setSearchTerm] = useState("");
  const [isScanning, setIsScanning] = useState(false);
  const [toastMsg, setToastMsg] = useState("");

  const handleRunScan = async () => {
     if (confirm("Executing a full S&P 500 scan will take 5-15 minutes. The process runs in the background on the server. Do you want to proceed?")) {
         setIsScanning(true);
         setToastMsg("");
         try {
             const res = await runSp500Screener();
             setToastMsg(res.message || "Scan started...");
         } catch (e: any) {
             setToastMsg("Error: " + e.message);
         } finally {
             setIsScanning(false);
         }
     }
  };

  const headerControls = (
      <div className="flex justify-between items-center mb-4 px-2">
          <div className="text-muted-text font-mono text-xs">
              {toastMsg && <span className="text-accent bg-accent/10 px-3 py-1 rounded inline-block">{toastMsg}</span>}
          </div>
          <button 
              onClick={handleRunScan}
              disabled={isScanning}
              className="bg-accent text-abyssal hover:bg-accent/90 px-4 py-1.5 text-xs font-mono uppercase font-bold transition-colors disabled:opacity-50 rounded"
          >
              {isScanning ? "Initializing..." : "Run Full S&P 500 Scan"}
          </button>
      </div>
  );

  if (!sp500Data || sp500Data.message) {
      return (
          <div className="p-6">
              {headerControls}
              <div className="flex items-center justify-center py-20">
                  <div className="text-muted-text font-mono text-sm max-w-md text-center border border-panel-light/30 p-6 rounded-md">
                      {sp500Data?.message || "No S&P 500 scanner reports found. Please generate one from the backend."}
                  </div>
              </div>
          </div>
      );
  }


  // Helper to format tables
  const renderTable = (data: any[], title: string, count: number) => {
    // Filter data based on search term
    const filtered = data.filter(stock => 
        (stock.Ticker || "").toLowerCase().includes(searchTerm.toLowerCase()) ||
        (stock.Sector || "").toLowerCase().includes(searchTerm.toLowerCase())
    ).slice(0, count);

    return (
      <div className="space-y-4">
        <div className="flex justify-between items-center bg-abyssal p-3 border border-panel-light/20 rounded">
            <h3 className="text-xs font-mono uppercase tracking-widest text-primary-text">{title}</h3>
            <input 
                type="text" 
                placeholder="Search Ticker/Sector..." 
                value={searchTerm}
                onChange={(e) => setSearchTerm(e.target.value)}
                className="bg-panel border border-panel-light text-primary-text font-mono text-xs px-3 py-1.5 focus:outline-none focus:border-accent uppercase placeholder:text-muted-text/40 w-64"
            />
        </div>
        
        <div className="overflow-x-auto rounded-md bg-panel border border-panel-light/30 p-2">
          <table className="w-full text-xs font-mono whitespace-nowrap">
            <thead>
              <tr className="border-b border-panel-light/30 text-muted-text uppercase tracking-wider text-left">
                <th className="py-2 px-3">Rank</th>
                <th className="py-2 px-3">Ticker</th>
                <th className="py-2 px-3">Price</th>
                <th className="py-2 px-3 text-right">Score/100</th>
                <th className="py-2 px-3 text-center">Rec.</th>
                <th className="py-2 px-3">Sector</th>
                <th className="py-2 px-3 text-right">Upside %</th>
                <th className="py-2 px-3">Risk Flags</th>
                <th className="py-2 px-3 text-right">Piotroski</th>
                <th className="py-2 px-3 text-right">Beneish</th>
                <th className="py-2 px-3 text-right">Altman</th>
              </tr>
            </thead>
            <tbody>
              {filtered.map((stock: any, i: number) => {
                const isBuy = stock.Recommendation === 'STRONG_BUY' || stock.Recommendation === 'BUY';
                const isSell = stock.Recommendation === 'SELL';
                
                return (
                  <tr key={`${stock.Ticker || 'unk'}-${i}`} className="border-b border-panel-light/10 hover:bg-panel-light/20 transition-colors">
                    <td className="py-2 px-3 text-muted-text">#{i + 1}</td>
                    <td className="py-2 px-3 font-medium text-accent">{stock.Ticker}</td>
                    <td className="py-2 px-3 text-primary-text">${Number(stock.Price).toFixed(2)}</td>
                    <td className={`py-2 px-3 text-right font-bold ${
                        Number(stock.Final_Score) >= 65 ? 'text-success' : Number(stock.Final_Score) <= 40 ? 'text-danger' : 'text-[#FFD700]'
                    }`}>
                        {Number(stock.Final_Score).toFixed(1)}
                    </td>
                    <td className={`py-2 px-3 text-center font-bold ${
                        isBuy ? 'text-success' : isSell ? 'text-danger' : 'text-[#FFD700]'
                    }`}>
                        <span className={`px-2 py-0.5 rounded-sm border ${
                            isBuy ? 'border-success/30 bg-success/10' : isSell ? 'border-danger/30 bg-danger/10' : 'border-[#FFD700]/30 bg-[#FFD700]/10'
                        }`}>
                            {stock.Recommendation}
                        </span>
                    </td>
                    <td className="py-2 px-3 text-muted-text truncate max-w-[120px]">{stock.Sector}</td>
                    <td className={`py-2 px-3 text-right ${
                        Number(stock.Upside_Pct) > 0 ? 'text-success' : 'text-danger'
                    }`}>
                        {Number(stock.Upside_Pct).toFixed(2)}%
                    </td>
                    <td className="py-2 px-3 text-muted-text truncate max-w-[150px]">
                        {stock.Risk_Flags && stock.Risk_Flags !== "N/A" ? (
                            <span className="text-danger flex items-center gap-1">
                                ⚠️ {String(stock.Risk_Flags).split(',')[0]}
                                {String(stock.Risk_Flags).split(',').length > 1 && '...'}
                            </span>
                        ) : '-'}
                    </td>
                    <td className="py-2 px-3 text-right">{stock.Piotroski_Score !== "N/A" ? stock.Piotroski_Score : '-'}</td>
                    <td className="py-2 px-3 text-right">{stock.Beneish_Score !== "N/A" ? Number(stock.Beneish_Score).toFixed(2) : '-'}</td>
                    <td className="py-2 px-3 text-right">{stock.Altman_Score !== "N/A" ? Number(stock.Altman_Score).toFixed(2) : '-'}</td>
                  </tr>
                );
              })}
            </tbody>
          </table>
          {filtered.length === 0 && (
             <div className="text-muted-text font-mono text-xs text-center py-8">No results match your search.</div>
          )}
        </div>
      </div>
    );
  };

  // Convert and sort data
  const data = Array.isArray(sp500Data) ? sp500Data : [];
  
  // Top Buys (Highest Final Score + BUY/STRONG_BUY)
  const topBuys = [...data]
    .filter(d => d.Recommendation === 'STRONG_BUY' || d.Recommendation === 'BUY')
    .sort((a, b) => Number(b.Final_Score) - Number(a.Final_Score));

  // Risk Flags (Has Accounting/Bankruptcy Risk)
  const highRisk = [...data]
    .filter(d => String(d.Risk_Flags).includes('RISK') || d.Recommendation === 'SELL')
    .sort((a, b) => Number(a.Final_Score) - Number(b.Final_Score));

  // Highest Upside  
  const topUpside = [...data]
    .sort((a, b) => Number(b.Upside_Pct) - Number(a.Upside_Pct));

  // All Rankings
  const allRankings = [...data]
    .sort((a, b) => Number(b.Final_Score) - Number(a.Final_Score));

  const tabs = [
    {
      id: "top_buys",
      label: "Top Buys",
      icon: "🏆",
      content: renderTable(topBuys, "Strong Fundamentals & High Scores", 50),
    },
    {
      id: "all_rankings",
      label: "All S&P 500 Rankings",
      icon: "📋",
      content: renderTable(allRankings, "Complete S&P 500 Scanner Results", 500),
    },
    {
      id: "top_upside",
      label: "Analyst Upside",
      icon: "📈",
      content: renderTable(topUpside, "Highest Analyst Target Upside", 50),
    },
    {
      id: "high_risk",
      label: "Risk Flags",
      icon: "⚠️",
      content: renderTable(highRisk, "Identified Bankruptcy or Accounting Risks", 50),
    },
  ];

  return (
    <div className="flex flex-col h-full p-4">
      {headerControls}
      <div className="flex-1 min-h-0 bg-panel border mx-2 rounded border-panel-light/30">
          <TabsContainer tabs={tabs} defaultTab="top_buys" />
      </div>
    </div>
  );
}
