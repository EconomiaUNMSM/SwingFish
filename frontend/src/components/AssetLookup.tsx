"use client";

import { useState } from "react";

export default function AssetLookup() {
  const [ticker, setTicker] = useState("");
  const [loading, setLoading] = useState(false);
  const [data, setData] = useState<any>(null);
  const [error, setError] = useState<string | null>(null);

  const handleSearch = async () => {
    if (!ticker.trim()) return;
    setLoading(true);
    setError(null);
    setData(null);

    try {
      const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || "http://127.0.0.1:8000/api/v1";
      const res = await fetch(`${API_BASE_URL}/dashboard/asset/${ticker.trim().toUpperCase()}`);
      if (!res.ok) throw new Error("Failed to fetch asset details");
      const json = await res.json();
      setData(json);
    } catch (e: any) {
      setError(e.message);
    } finally {
      setLoading(false);
    }
  };

  const info = data?.general_info;
  const insider = data?.insider_data;

  return (
    <div className="rounded-md bg-panel border border-panel-light/30 p-5">
      <h2 className="text-xs uppercase tracking-widest text-muted-text font-mono mb-4 flex items-center gap-2">
        <span className="w-2 h-2 rounded-full bg-accent"></span>
        Asset Intelligence & Insider Trading
      </h2>

      {/* Search Bar */}
      <div className="flex gap-2 mb-5">
        <input
          type="text"
          value={ticker}
          onChange={(e) => setTicker(e.target.value.toUpperCase())}
          onKeyDown={(e) => e.key === "Enter" && handleSearch()}
          placeholder="Enter ticker (AAPL, MSFT, NVDA...)"
          className="flex-1 bg-abyssal border border-panel-light text-primary-text font-mono text-xs px-4 py-2.5 focus:outline-none focus:border-accent uppercase placeholder:text-muted-text/40"
        />
        <button
          onClick={handleSearch}
          disabled={loading}
          className="bg-accent text-abyssal hover:bg-accent/90 px-6 py-2.5 text-xs font-mono uppercase font-bold transition-colors disabled:opacity-50"
        >
          {loading ? "SCANNING..." : "ANALYZE"}
        </button>
      </div>

      {/* Loading */}
      {loading && (
        <div className="flex items-center justify-center py-12">
          <div className="w-6 h-6 border-2 border-accent/30 border-t-accent rounded-full animate-spin"></div>
          <span className="ml-3 text-muted-text font-mono text-xs">Fetching intelligence for {ticker}...</span>
        </div>
      )}

      {/* Error */}
      {error && (
        <div className="text-danger font-mono text-xs py-4 text-center">{error}</div>
      )}

      {/* Results */}
      {data && !loading && (
        <div className="space-y-5">
          {/* General Info */}
          {info && (
            <div className="grid grid-cols-2 md:grid-cols-4 gap-3">
              <div className="bg-abyssal rounded p-3 border border-panel-light/20">
                <div className="text-[10px] text-muted-text uppercase font-mono">Company</div>
                <div className="text-sm text-primary-text font-medium mt-1 truncate">{info.nombre || data.ticker}</div>
              </div>
              <div className="bg-abyssal rounded p-3 border border-panel-light/20">
                <div className="text-[10px] text-muted-text uppercase font-mono">Current Price</div>
                <div className="text-xl text-accent font-mono font-bold mt-1">${info.precio_actual || 'N/A'}</div>
              </div>
              <div className="bg-abyssal rounded p-3 border border-panel-light/20">
                <div className="text-[10px] text-muted-text uppercase font-mono">Recommendation</div>
                <div className={`text-lg font-mono font-bold mt-1 uppercase ${
                  info.recomendacion === 'buy' || info.recomendacion === 'strong_buy' ? 'text-success' :
                  info.recomendacion === 'sell' ? 'text-danger' : 'text-[#FFD700]'
                }`}>{info.recomendacion || 'N/A'}</div>
              </div>
              <div className="bg-abyssal rounded p-3 border border-panel-light/20">
                <div className="text-[10px] text-muted-text uppercase font-mono">Beta</div>
                <div className="text-xl text-primary-text font-mono font-bold mt-1">{info.beta || 'N/A'}</div>
              </div>
            </div>
          )}

          {/* Analyst Estimates */}
          {info && (
            <div className="grid grid-cols-3 gap-3">
              <div className="bg-abyssal rounded p-3 border border-panel-light/20 text-center">
                <div className="text-[10px] text-muted-text uppercase font-mono">Target Low</div>
                <div className="text-lg text-danger font-mono font-bold mt-1">${info.estimacion_baja || '-'}</div>
              </div>
              <div className="bg-abyssal rounded p-3 border border-panel-light/20 text-center">
                <div className="text-[10px] text-muted-text uppercase font-mono">Target Mean</div>
                <div className="text-lg text-[#FFD700] font-mono font-bold mt-1">${info.estimacion_media || '-'}</div>
              </div>
              <div className="bg-abyssal rounded p-3 border border-panel-light/20 text-center">
                <div className="text-[10px] text-muted-text uppercase font-mono">Target High</div>
                <div className="text-lg text-success font-mono font-bold mt-1">${info.estimacion_alta || '-'}</div>
              </div>
            </div>
          )}

          {/* Ownership */}
          {info && (
            <div className="grid grid-cols-2 gap-3">
              <div className="bg-abyssal rounded p-3 border border-panel-light/20">
                <div className="text-[10px] text-muted-text uppercase font-mono">Insiders Ownership</div>
                <div className="text-lg text-primary-text font-mono font-bold mt-1">{info.insiders_prop !== 'N/A' ? info.insiders_prop + '%' : 'N/A'}</div>
              </div>
              <div className="bg-abyssal rounded p-3 border border-panel-light/20">
                <div className="text-[10px] text-muted-text uppercase font-mono">Institutional Ownership</div>
                <div className="text-lg text-primary-text font-mono font-bold mt-1">{info.inst_prop !== 'N/A' ? info.inst_prop + '%' : 'N/A'}</div>
              </div>
            </div>
          )}

          {/* Insider Transactions */}
          {insider?.has_insider_transactions && insider.insider_transactions.length > 0 && (
            <div>
              <h3 className="text-xs uppercase tracking-widest text-accent font-mono mb-3 border-b border-panel-light/30 pb-2">
                Insider Transactions
              </h3>
              <div className="overflow-x-auto">
                <table className="w-full text-xs font-mono">
                  <thead>
                    <tr className="border-b border-panel-light/30 text-muted-text uppercase tracking-wider">
                      <th className="py-2 px-2 text-left">Date</th>
                      <th className="py-2 px-2 text-left">Insider</th>
                      <th className="py-2 px-2 text-left">Title</th>
                      <th className="py-2 px-2 text-left">Type</th>
                      <th className="py-2 px-2 text-right">Shares</th>
                      <th className="py-2 px-2 text-right">Value</th>
                    </tr>
                  </thead>
                  <tbody>
                    {insider.insider_transactions.slice(0, 20).map((tx: any, i: number) => {
                      const isSell = (tx.transactionType || tx.disposition || '').toLowerCase().includes('sell') ||
                                     (tx.transactionType || tx.disposition || '').toLowerCase().includes('sale');
                      return (
                        <tr key={i} className="border-b border-panel-light/10 hover:bg-panel-light/20 transition-colors">
                          <td className="py-2 px-2 text-muted-text">{tx.startDate || tx.date || '-'}</td>
                          <td className="py-2 px-2 text-primary-text font-medium max-w-[150px] truncate">{tx.filerName || tx.insider || '-'}</td>
                          <td className="py-2 px-2 text-muted-text max-w-[120px] truncate">{tx.filerRelation || tx.position || '-'}</td>
                          <td className={`py-2 px-2 font-medium ${isSell ? 'text-danger' : 'text-success'}`}>
                            {tx.transactionType || tx.ownership || '-'}
                          </td>
                          <td className="py-2 px-2 text-right text-primary-text">{tx.shares ? Number(tx.shares).toLocaleString('en-US') : '-'}</td>
                          <td className="py-2 px-2 text-right text-primary-text">{tx.value ? '$' + Number(tx.value).toLocaleString('en-US') : '-'}</td>
                        </tr>
                      );
                    })}
                  </tbody>
                </table>
              </div>
            </div>
          )}

          {/* Institutional Ownership */}
          {insider?.has_institutional_ownership && insider.institutional_ownership.length > 0 && (
            <div>
              <h3 className="text-xs uppercase tracking-widest text-[#00C2FF] font-mono mb-3 border-b border-panel-light/30 pb-2">
                Top Institutional Holders
              </h3>
              <div className="overflow-x-auto">
                <table className="w-full text-xs font-mono">
                  <thead>
                    <tr className="border-b border-panel-light/30 text-muted-text uppercase tracking-wider">
                      <th className="py-2 px-2 text-left">Institution</th>
                      <th className="py-2 px-2 text-right">Shares</th>
                      <th className="py-2 px-2 text-right">% Held</th>
                      <th className="py-2 px-2 text-right">Value</th>
                      <th className="py-2 px-2 text-left">Report Date</th>
                    </tr>
                  </thead>
                  <tbody>
                    {insider.institutional_ownership.slice(0, 15).map((inst: any, i: number) => (
                      <tr key={i} className="border-b border-panel-light/10 hover:bg-panel-light/20 transition-colors">
                        <td className="py-2 px-2 text-primary-text font-medium max-w-[200px] truncate">{inst.organization || '-'}</td>
                        <td className="py-2 px-2 text-right text-primary-text">{inst.position ? Number(inst.position).toLocaleString('en-US') : '-'}</td>
                        <td className="py-2 px-2 text-right text-accent">{inst.pctHeld ? (inst.pctHeld * 100).toFixed(2) + '%' : '-'}</td>
                        <td className="py-2 px-2 text-right text-primary-text">{inst.value ? '$' + Number(inst.value).toLocaleString('en-US') : '-'}</td>
                        <td className="py-2 px-2 text-muted-text">{inst.reportDate || '-'}</td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </div>
          )}

          {/* No insider data message */}
          {insider && !insider.has_insider_transactions && !insider.has_institutional_ownership && (
            <div className="text-muted-text font-mono text-xs text-center py-6 border border-panel-light/20 rounded">
              No insider or institutional ownership data available for {data.ticker}.
            </div>
          )}
        </div>
      )}

      {/* Empty State */}
      {!data && !loading && !error && (
        <div className="text-center py-10 text-muted-text font-mono text-sm opacity-50">
          ENTER A TICKER ABOVE TO RETRIEVE ASSET INTELLIGENCE, INSIDER TRANSACTIONS & INSTITUTIONAL OWNERSHIP.
        </div>
      )}
    </div>
  );
}
