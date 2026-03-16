"use client";

import {
  ResponsiveContainer,
  AreaChart,
  Area,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
} from "recharts";

interface Props {
  data: { dates: string[]; values: number[] } | null;
  color?: string;
  label?: string;
}

export default function MacroLineChart({ data, color = "#00C2FF", label = "Value" }: Props) {
  if (!data || !data.dates) {
    return <div className="text-muted-text font-mono text-xs text-center py-8">No data available.</div>;
  }

  const chartData = data.dates.map((date, i) => ({
    date: date.slice(0, 7),
    value: data.values[i],
  }));

  return (
    <ResponsiveContainer width="100%" height={220}>
      <AreaChart data={chartData} margin={{ top: 5, right: 10, left: 0, bottom: 5 }}>
        <defs>
          <linearGradient id={`gradient-${color.replace("#", "")}`} x1="0" y1="0" x2="0" y2="1">
            <stop offset="5%" stopColor={color} stopOpacity={0.3} />
            <stop offset="95%" stopColor={color} stopOpacity={0.02} />
          </linearGradient>
        </defs>
        <CartesianGrid strokeDasharray="3 3" stroke="#172A3A" />
        <XAxis dataKey="date" tick={{ fill: "#8B9DAE", fontSize: 10 }} tickLine={false} />
        <YAxis tick={{ fill: "#8B9DAE", fontSize: 10 }} tickLine={false} domain={["auto", "auto"]} />
        <Tooltip
          contentStyle={{ backgroundColor: "#11202D", border: "1px solid #172A3A", borderRadius: 4, fontSize: 12 }}
          labelStyle={{ color: "#8B9DAE" }}
        />
        <Area
          type="monotone"
          dataKey="value"
          stroke={color}
          strokeWidth={2}
          fill={`url(#gradient-${color.replace("#", "")})`}
          name={label}
        />
      </AreaChart>
    </ResponsiveContainer>
  );
}
