"use client";

import TabsContainer from "./TabsContainer";
import AssetLookup from "./AssetLookup";

interface Props {
  scannerData: any;
  calendarData: any;
}

export default function ScannerDashboard({ scannerData, calendarData }: Props) {
  const scannerColumns = ["Ticker", "Company", "Sector", "Market Cap", "P/E", "Price", "Change", "Volume"];

  const renderTable = (data: any[]) => (
    <div className="overflow-x-auto">
      <table className="w-full text-xs font-mono">
        <thead>
          <tr className="border-b border-panel-light/30 text-muted-text uppercase tracking-wider">
            {scannerColumns.map(col => (
              <th key={col} className={`py-2 px-3 ${col === 'Company' || col === 'Ticker' ? 'text-left' : 'text-right'} whitespace-nowrap`}>{col}</th>
            ))}
          </tr>
        </thead>
        <tbody>
          {data.slice(0, 30).map((stock: any, i: number) => (
            <tr key={i} className="border-b border-panel-light/10 hover:bg-panel-light/20 transition-colors">
              <td className="py-1.5 px-3 text-accent font-medium">{stock.Ticker}</td>
              <td className="py-1.5 px-3 text-primary-text max-w-[180px] truncate">{stock.Company || stock["Company Name"] || '-'}</td>
              <td className="py-1.5 px-3 text-muted-text text-right max-w-[100px] truncate">{stock.Sector || '-'}</td>
              <td className="py-1.5 px-3 text-right text-primary-text whitespace-nowrap">{stock["Market Cap"] ? Number(stock["Market Cap"]).toLocaleString('en-US') : '-'}</td>
              <td className="py-1.5 px-3 text-right text-muted-text">{stock["P/E"] || '-'}</td>
              <td className="py-1.5 px-3 text-right text-primary-text">${stock.Price}</td>
              <td className={`py-1.5 px-3 text-right font-medium ${Number(stock.Change) >= 0 ? 'text-success' : 'text-danger'}`}>
                {Number(stock.Change) >= 0 ? '+' : ''}{stock.Change}%
              </td>
              <td className="py-1.5 px-3 text-right text-muted-text whitespace-nowrap">{stock.Volume ? Number(stock.Volume).toLocaleString('en-US') : '-'}</td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );

  const tabs = [
    {
      id: "asset",
      label: "Asset Intel",
      icon: "🎯",
      content: <AssetLookup />,
    },
    {
      id: "active",
      label: "Most Active",
      icon: "🟢",
      content: scannerData?.most_active?.length > 0
        ? renderTable(scannerData.most_active)
        : <div className="text-muted-text font-mono text-xs text-center py-8">No data available.</div>,
    },
    {
      id: "volatile",
      label: "Most Volatile",
      icon: "🔴",
      content: scannerData?.most_volatile?.length > 0
        ? renderTable(scannerData.most_volatile)
        : <div className="text-muted-text font-mono text-xs text-center py-8">No data available.</div>,
    },
    {
      id: "calendar",
      label: "Econ Calendar",
      icon: "📅",
      content: calendarData && Array.isArray(calendarData) && calendarData.length > 0 ? (
        <div className="overflow-x-auto">
          <table className="w-full text-xs font-mono">
            <thead>
              <tr className="border-b border-panel-light/30 text-muted-text uppercase tracking-wider">
                <th className="py-2 px-3 text-left">Date</th>
                <th className="py-2 px-3 text-left">Time</th>
                <th className="py-2 px-3 text-left">Currency</th>
                <th className="py-2 px-3 text-left">Event</th>
                <th className="py-2 px-3 text-right">Forecast</th>
                <th className="py-2 px-3 text-right">Previous</th>
              </tr>
            </thead>
            <tbody>
              {calendarData.map((ev: any, i: number) => (
                <tr key={i} className="border-b border-panel-light/10 hover:bg-panel-light/20 transition-colors">
                  <td className="py-2 px-3 text-accent">{ev.fecha}</td>
                  <td className="py-2 px-3 text-muted-text">{ev.hora}</td>
                  <td className="py-2 px-3 text-primary-text">{ev.moneda}</td>
                  <td className="py-2 px-3 text-primary-text font-medium">{ev.evento}</td>
                  <td className="py-2 px-3 text-right text-accent">{ev.esperado || '-'}</td>
                  <td className="py-2 px-3 text-right text-muted-text">{ev.previo || '-'}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      ) : (
        <div className="text-muted-text font-mono text-xs text-center py-8">No high-impact events this week.</div>
      ),
    },
  ];

  return <TabsContainer tabs={tabs} defaultTab="asset" />;
}
