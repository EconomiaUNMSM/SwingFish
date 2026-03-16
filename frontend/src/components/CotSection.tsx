"use client";

import { useState, useMemo } from "react";
import CotChart from "./charts/CotChart";

interface CotContracts {
  currencies: string[];
  indices: string[];
  crypto: string[];
  rates: string[];
}

interface Props {
  initialData: any[] | null;
  contracts: CotContracts | null;
}

export default function CotSection({ initialData, contracts }: Props) {
  const [cotData, setCotData] = useState(initialData);
  const [selectedMarket, setSelectedMarket] = useState("E-MINI S&P 500 - CHICAGO MERCANTILE EXCHANGE");
  const [searchTerm, setSearchTerm] = useState("");
  const [isOpen, setIsOpen] = useState(false);
  const [loading, setLoading] = useState(false);

  // Flatten all contracts into a single list
  const allContracts = useMemo(() => {
    if (!contracts) return [];
    return [
      ...contracts.indices.map(c => ({ name: c, group: "Indices" })),
      ...contracts.currencies.map(c => ({ name: c, group: "Currencies" })),
      ...contracts.crypto.map(c => ({ name: c, group: "Crypto" })),
      ...contracts.rates.map(c => ({ name: c, group: "Rates & VIX" })),
    ];
  }, [contracts]);

  // Filter by search term (similarity)
  const filteredContracts = useMemo(() => {
    if (!searchTerm) return allContracts;
    const lower = searchTerm.toLowerCase();
    return allContracts.filter(c => c.name.toLowerCase().includes(lower));
  }, [allContracts, searchTerm]);

  const handleSelect = async (market: string) => {
    setSelectedMarket(market);
    setIsOpen(false);
    setSearchTerm("");
    setLoading(true);

    try {
      const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || "http://127.0.0.1:8000/api/v1";
      const res = await fetch(`${API_BASE_URL}/dashboard/macro/cot?market=${encodeURIComponent(market)}`);
      if (res.ok) {
        const data = await res.json();
        setCotData(data);
      }
    } catch (e) {
      console.error(e);
    } finally {
      setLoading(false);
    }
  };

  // Extract short label from full market name
  const shortLabel = selectedMarket.split(" - ")[0];

  return (
    <div>
      <div className="flex items-center justify-between mb-4">
        <h2 className="text-xs uppercase tracking-widest text-muted-text font-mono">
          COT Net Positioning
        </h2>
        
        {/* Dropdown */}
        <div className="relative">
          <button
            onClick={() => setIsOpen(!isOpen)}
            className="bg-abyssal border border-panel-light text-primary-text font-mono text-xs px-3 py-1.5 rounded hover:border-accent transition-colors flex items-center gap-2 max-w-xs truncate"
          >
            <span className="truncate">{shortLabel}</span>
            <svg className={`w-3 h-3 transition-transform ${isOpen ? 'rotate-180' : ''}`} fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 9l-7 7-7-7" />
            </svg>
          </button>
          
          {isOpen && (
            <div className="absolute right-0 top-full mt-1 w-96 bg-panel border border-panel-light rounded shadow-2xl z-50 max-h-80 flex flex-col">
              <input
                type="text"
                placeholder="Search contract..."
                value={searchTerm}
                onChange={(e) => setSearchTerm(e.target.value)}
                className="bg-abyssal border-b border-panel-light text-primary-text font-mono text-xs px-3 py-2 focus:outline-none focus:border-accent w-full"
                autoFocus
              />
              <div className="overflow-y-auto flex-1">
                {filteredContracts.length === 0 ? (
                  <div className="px-3 py-2 text-muted-text text-xs font-mono">No matches found.</div>
                ) : (
                  <>
                    {/* Group by category */}
                    {["Indices", "Currencies", "Crypto", "Rates & VIX"].map(group => {
                      const items = filteredContracts.filter(c => c.group === group);
                      if (items.length === 0) return null;
                      return (
                        <div key={group}>
                          <div className="px-3 py-1 text-muted-text/60 text-[10px] uppercase tracking-wider font-mono bg-abyssal/50 sticky top-0">{group}</div>
                          {items.map((contract) => (
                            <button
                              key={contract.name}
                              onClick={() => handleSelect(contract.name)}
                              className={`w-full text-left px-3 py-1.5 text-xs font-mono hover:bg-panel-light/40 transition-colors truncate ${
                                contract.name === selectedMarket ? 'text-accent bg-panel-light/20' : 'text-primary-text'
                              }`}
                            >
                              {contract.name.split(" - ")[0]}
                            </button>
                          ))}
                        </div>
                      );
                    })}
                  </>
                )}
              </div>
            </div>
          )}
        </div>
      </div>

      {loading ? (
        <div className="flex items-center justify-center h-[280px]">
          <div className="w-6 h-6 border-2 border-accent/30 border-t-accent rounded-full animate-spin"></div>
          <span className="ml-3 text-muted-text font-mono text-xs">Loading COT data...</span>
        </div>
      ) : (
        <CotChart data={cotData} />
      )}
    </div>
  );
}
