"use client";

import TabsContainer from "./TabsContainer";
import UnemploymentChart from "./charts/UnemploymentChart";
import MacroLineChart from "./charts/MacroLineChart";
import CotSection from "./CotSection";

interface Props {
  macroData: any;
  cotData: any;
  cotContracts: any;
}

export default function MacroDashboard({ macroData, cotData, cotContracts }: Props) {
  // Latest readings for summary cards
  const latestUnemployment = macroData?.unemployment_vs_sp500
    ? macroData.unemployment_vs_sp500.unemployment_rate[macroData.unemployment_vs_sp500.unemployment_rate.length - 1]
    : null;
  const latestSP500 = macroData?.unemployment_vs_sp500
    ? macroData.unemployment_vs_sp500.sp500_close[macroData.unemployment_vs_sp500.sp500_close.length - 1]
    : null;
  const latestCPI = macroData?.cpi
    ? macroData.cpi.values[macroData.cpi.values.length - 1]
    : null;
  const latestGDP = macroData?.gdp
    ? macroData.gdp.values[macroData.gdp.values.length - 1]
    : null;

  const tabs = [
    {
      id: "unemployment",
      label: "Unemployment vs S&P",
      icon: "📉",
      content: (
        <div className="space-y-4">
          <div className="grid grid-cols-2 gap-3">
            <div className="bg-abyssal rounded p-3 border border-panel-light/20">
              <div className="text-[10px] text-muted-text uppercase font-mono">Unemployment Rate</div>
              <div className="text-2xl text-danger font-semibold font-mono mt-1">{latestUnemployment ? latestUnemployment + '%' : 'N/A'}</div>
            </div>
            <div className="bg-abyssal rounded p-3 border border-panel-light/20">
              <div className="text-[10px] text-muted-text uppercase font-mono">S&P 500</div>
              <div className="text-2xl text-success font-semibold font-mono mt-1">{latestSP500 ? '$' + latestSP500.toLocaleString('en-US') : 'N/A'}</div>
            </div>
          </div>
          <UnemploymentChart data={macroData?.unemployment_vs_sp500 || null} />
        </div>
      ),
    },
    {
      id: "cot",
      label: "COT Positioning",
      icon: "📊",
      content: <CotSection initialData={cotData} contracts={cotContracts} />,
    },
    {
      id: "indicators",
      label: "Macro Indicators",
      icon: "🌐",
      content: (
        <div className="space-y-4">
          <div className="grid grid-cols-2 gap-3">
            <div className="bg-abyssal rounded p-3 border border-panel-light/20">
              <div className="text-[10px] text-muted-text uppercase font-mono">CPI Index</div>
              <div className="text-2xl text-primary-text font-semibold font-mono mt-1">{latestCPI ?? 'N/A'}</div>
            </div>
            <div className="bg-abyssal rounded p-3 border border-panel-light/20">
              <div className="text-[10px] text-muted-text uppercase font-mono">GDP (Nominal)</div>
              <div className="text-2xl text-primary-text font-semibold font-mono mt-1">{latestGDP ? '$' + latestGDP.toLocaleString('en-US') + 'B' : 'N/A'}</div>
            </div>
          </div>
          <div className="grid grid-cols-1 lg:grid-cols-3 gap-4">
            <div className="rounded-md bg-abyssal border border-panel-light/20 p-4">
              <h3 className="text-[10px] uppercase tracking-widest text-muted-text font-mono mb-2">CPI Inflation</h3>
              <MacroLineChart data={macroData?.cpi || null} color="#FF4D4D" label="CPI" />
            </div>
            <div className="rounded-md bg-abyssal border border-panel-light/20 p-4">
              <h3 className="text-[10px] uppercase tracking-widest text-muted-text font-mono mb-2">Consumer Confidence</h3>
              <MacroLineChart data={macroData?.consumer_confidence || null} color="#00C2FF" label="UMich" />
            </div>
            <div className="rounded-md bg-abyssal border border-panel-light/20 p-4">
              <h3 className="text-[10px] uppercase tracking-widest text-muted-text font-mono mb-2">GDP (Nominal)</h3>
              <MacroLineChart data={macroData?.gdp || null} color="#00FFA3" label="GDP" />
            </div>
          </div>
        </div>
      ),
    },
    {
      id: "real_gdp",
      label: "Real GDP",
      icon: "💹",
      content: (
        <div>
          <MacroLineChart data={macroData?.real_gdp || null} color="#FFD700" label="Real GDP Growth %" />
        </div>
      ),
    },
  ];

  return <TabsContainer tabs={tabs} defaultTab="unemployment" />;
}
