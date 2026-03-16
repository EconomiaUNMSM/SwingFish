"use client";

import {
  ResponsiveContainer,
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Cell,
  ReferenceLine,
} from "recharts";

interface CotRecord {
  "Report_Date_as_YYYY-MM-DD": string;
  Net_COT: number;
  [key: string]: any;
}

interface Props {
  data: CotRecord[] | null;
}

export default function CotChart({ data }: Props) {
  if (!data || !Array.isArray(data) || data.length === 0 || data[0]?.error) {
    return <div className="text-muted-text font-mono text-xs text-center py-8">No COT data available.</div>;
  }

  const chartData = data.map((item) => ({
    date: item["Report_Date_as_YYYY-MM-DD"]?.slice(5) || "", // MM-DD
    netCot: Number(item.Net_COT?.toFixed(2)) || 0,
  }));

  return (
    <ResponsiveContainer width="100%" height={280}>
      <BarChart data={chartData} margin={{ top: 5, right: 10, left: 0, bottom: 5 }}>
        <CartesianGrid strokeDasharray="3 3" stroke="#172A3A" />
        <XAxis dataKey="date" tick={{ fill: "#8B9DAE", fontSize: 10 }} tickLine={false} />
        <YAxis tick={{ fill: "#8B9DAE", fontSize: 10 }} tickLine={false} />
        <Tooltip
          contentStyle={{ backgroundColor: "#11202D", border: "1px solid #172A3A", borderRadius: 4, fontSize: 12 }}
          labelStyle={{ color: "#8B9DAE" }}
        />
        <ReferenceLine y={0} stroke="#8B9DAE" strokeDasharray="3 3" />
        <Bar dataKey="netCot" name="Net COT" radius={[2, 2, 0, 0]}>
          {chartData.map((entry, index) => (
            <Cell key={`cell-${index}`} fill={entry.netCot >= 0 ? "#00FFA3" : "#FF4D4D"} />
          ))}
        </Bar>
      </BarChart>
    </ResponsiveContainer>
  );
}
