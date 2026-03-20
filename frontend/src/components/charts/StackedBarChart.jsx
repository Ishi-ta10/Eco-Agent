import React from "react";
import {
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  ResponsiveContainer,
} from "recharts";

export const StackedBarChart = ({
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
        <BarChart
          data={data}
          margin={{ top: 20, right: 30, left: 0, bottom: 20 }}
        >
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
            <Bar
              key={key}
              dataKey={key}
              fill={colors[idx]}
              stackId="a"
              radius={[4, 4, 0, 0]}
            />
          ))}
        </BarChart>
      </ResponsiveContainer>
    </div>
  );
};
