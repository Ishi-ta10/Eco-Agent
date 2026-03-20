import React from "react";
import {
  PieChart,
  Pie,
  Cell,
  Tooltip,
  ResponsiveContainer,
  Legend,
} from "recharts";

export const DonutChart = ({ data, title, colors }) => {
  return (
    <div className="surface-card rounded-2xl p-6">
      <h3 className="text-xl font-bold section-title mb-6">{title}</h3>
      <ResponsiveContainer width="100%" height={320}>
        <PieChart>
          <Pie
            data={data}
            dataKey="value"
            nameKey="name"
            innerRadius={64}
            outerRadius={102}
            paddingAngle={2}
            stroke="none"
            isAnimationActive={true}
          >
            {data.map((entry, index) => (
              <Cell
                key={`${entry.name}-${index}`}
                fill={colors[index % colors.length]}
              />
            ))}
          </Pie>
          <Tooltip
            contentStyle={{
              backgroundColor: "var(--surface)",
              border: "1px solid var(--surface-border)",
              borderRadius: "12px",
              boxShadow: "var(--shadow)",
            }}
            labelStyle={{ color: "var(--text-primary)" }}
            formatter={(value) =>
              `${Number(value).toLocaleString("en-IN", { maximumFractionDigits: 1 })}%`
            }
          />
          <Legend wrapperStyle={{ color: "var(--text-muted)" }} />
        </PieChart>
      </ResponsiveContainer>
    </div>
  );
};
