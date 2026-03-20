import React from "react";
import {
  AreaChart,
  Area,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  ResponsiveContainer,
} from "recharts";

export const AreaChartComponent = ({
  data,
  title,
  dataKeys,
  colors,
  xDataKey = "Date",
}) => {
  return (
    <div className="surface-card rounded-2xl p-6">
      <h3 className="text-xl font-bold section-title mb-6">{title}</h3>
      <ResponsiveContainer width="100%" height={350}>
        <AreaChart
          data={data}
          margin={{ top: 20, right: 30, left: 0, bottom: 20 }}
        >
          <defs>
            {colors.map((color, idx) => (
              <linearGradient
                key={idx}
                id={`color${idx}`}
                x1="0"
                y1="0"
                x2="0"
                y2="1"
              >
                <stop offset="5%" stopColor={color} stopOpacity={0.8} />
                <stop offset="95%" stopColor={color} stopOpacity={0.1} />
              </linearGradient>
            ))}
          </defs>
          <CartesianGrid strokeDasharray="3 3" stroke="var(--surface-border)" />
          <XAxis
            dataKey={xDataKey}
            stroke="var(--text-muted)"
            style={{ fontSize: "12px" }}
          />
          <YAxis stroke="var(--text-muted)" style={{ fontSize: "12px" }} />
          <Tooltip
            contentStyle={{
              backgroundColor: "var(--surface)",
              border: "1px solid var(--surface-border)",
              borderRadius: "12px",
              boxShadow: "var(--shadow)",
            }}
            labelStyle={{ color: "var(--text-primary)" }}
            formatter={(value) =>
              value.toLocaleString("en-IN", { maximumFractionDigits: 2 })
            }
          />
          <Legend
            wrapperStyle={{ paddingTop: "20px" }}
            contentStyle={{ color: "var(--text-muted)" }}
          />
          {dataKeys.map((key, idx) => (
            <Area
              key={key}
              type="monotone"
              dataKey={key}
              stroke={colors[idx]}
              strokeWidth={2}
              fillOpacity={0.7}
              fill={`url(#color${idx})`}
              isAnimationActive={true}
            />
          ))}
        </AreaChart>
      </ResponsiveContainer>
    </div>
  );
};
