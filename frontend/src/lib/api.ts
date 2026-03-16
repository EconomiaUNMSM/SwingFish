/**
 * API Wrapper for SwingFish Backend.
 * Simplifies fetching from FastAPI server and manages types.
 */

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || "http://127.0.0.1:8000/api/v1";

export async function fetchWithTimeout(resource: string, options: RequestInit & { timeout?: number } = {}) {
  const { timeout = 120000 } = options;
  
  const controller = new AbortController();
  const id = setTimeout(() => controller.abort(), timeout);
  
  const response = await fetch(`${API_BASE_URL}${resource}`, {
    ...options,
    signal: controller.signal  
  });
  
  clearTimeout(id);
  return response;
}

// -------------------------------------------------------------
// DASHBOARD ENDPOINTS
// -------------------------------------------------------------

export async function getMacroEvents() {
    try {
        const res = await fetchWithTimeout('/dashboard/macro/events');
        if (!res.ok) throw new Error("Failed connecting to macro events API");
        return await res.json();
    } catch (e) {
        console.error(e);
        return null;
    }
}

export async function getCotReport(market?: string) {
    try {
        const params = market ? `?market=${encodeURIComponent(market)}` : '';
        const res = await fetchWithTimeout(`/dashboard/macro/cot${params}`);
        if (!res.ok) throw new Error("Failed connecting to COT API");
        return await res.json();
    } catch (e) {
        console.error(e);
        return null;
    }
}

export async function getCotContracts() {
    try {
        const res = await fetchWithTimeout('/dashboard/macro/cot/contracts');
        if (!res.ok) throw new Error("Failed fetching COT contracts");
        return await res.json();
    } catch (e) {
        console.error(e);
        return null;
    }
}

export async function getMarketScanner() {
    try {
        const res = await fetchWithTimeout('/dashboard/scanner');
        if (!res.ok) throw new Error("Failed connecting to Scanner API");
        return await res.json();
    } catch (e) {
        console.error(e);
        return null;
    }
}

export async function getEconomicCalendar() {
    try {
        const res = await fetchWithTimeout('/dashboard/macro/calendar');
        if (!res.ok) throw new Error("Failed connecting to Calendar API");
        return await res.json();
    } catch (e) {
        console.error(e);
        return null;
    }
}

export async function getAssetDetails(ticker: string) {
    try {
        const res = await fetchWithTimeout(`/dashboard/asset/${ticker}`);
        if (!res.ok) throw new Error("Failed fetching asset details");
        return await res.json();
    } catch (e) {
        console.error(e);
        return null;
    }
}

export async function getSp500ScreenerResults() {
    try {
        const res = await fetchWithTimeout('/screener/sp500', { timeout: 300000 });
        if (!res.ok) throw new Error("Failed fetching SP500 screener results");
        return await res.json();
    } catch (e) {
        console.error(e);
        return null;
    }
}

export async function runSp500Screener() {
    const res = await fetchWithTimeout('/screener/sp500/run', {
        method: "POST"
    });
    
    if (!res.ok) {
        const text = await res.text();
        throw new Error(`Failed to start scan: ${text}`);
    }
    
    return await res.json();
}

// -------------------------------------------------------------
// ANALYSIS ENDPOINTS
// -------------------------------------------------------------
export async function runMultiagentAnalysis(ticker: string, language: string = "en") {
    const res = await fetchWithTimeout(`/analysis/multiagent/${ticker}?language=${language}`, {
        method: "POST"
    });
    
    if (!res.ok) {
        const text = await res.text();
        throw new Error(`Analysis failed: ${text}`);
    }
    
    return await res.json();
}
