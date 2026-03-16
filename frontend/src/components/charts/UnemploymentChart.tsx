"use client";

import {
  ResponsiveContainer,
  LineChart,
  Line,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
} from "recharts";

interface Props {
  data: {
    dates: string[];
    unemployment_rate: number[];
    sp500_close: number[];
  } | null;
}

export default function UnemploymentChart({ data }: Props) {
  if (!data || !data.dates) {
    return <div className="text-muted-text font-mono text-xs text-center py-8">No unemployment data available.</div>;
  }

  const chartData = data.dates.map((date, i) => ({
    date: date.slice(0, 7), // YYYY-MM
    unemployment: data.unemployment_rate[i],
    sp500: data.sp500_close[i],
  }));

  return (
    <ResponsiveContainer width="100%" height={280}>
      <LineChart data={chartData} margin={{ top: 5, right: 10, left: 0, bottom: 5 }}>
        <CartesianGrid strokeDasharray="3 3" stroke="#172A3A" />
        <XAxis dataKey="date" tick={{ fill: "#8B9DAE", fontSize: 10 }} tickLine={false} />
        <YAxis yAxisId="left" tick={{ fill: "#FF4D4D", fontSize: 10 }} tickLine={false} domain={["auto", "auto"]} />
        <YAxis yAxisId="right" orientation="right" tick={{ fill: "#00FFA3", fontSize: 10 }} tickLine={false} domain={["auto", "auto"]} />
        <Tooltip
          contentStyle={{ backgroundColor: "#11202D", border: "1px solid #172A3A", borderRadius: 4, fontSize: 12 }}
          labelStyle={{ color: "#8B9DAE" }}
        />
        <Legend wrapperStyle={{ fontSize: 11, color: "#8B9DAE" }} />
        <Line yAxisId="left" type="monotone" dataKey="unemployment" stroke="#FF4D4D" strokeWidth={2} dot={false} name="Unemployment %" />
        <Line yAxisId="right" type="monotone" dataKey="sp500" stroke="#00FFA3" strokeWidth={2} dot={false} name="S&P 500" />
      </LineChart>
    </ResponsiveContainer>
  );
}
