import React from "react";
import { TrendingUp, TrendingDown } from "lucide-react";

export const KPICard = ({
  title,
  value,
  unit = "",
  delta = null,
  deltaLabel = "",
  icon: Icon = null,
  color = "blue",
}) => {
  const colorClasses = {
    blue: "from-[#ecf3fb] to-[#e8eff9] border-[#c9d8ea] hover:border-[#a5bdd8]",
    green:
      "from-[#ebfaf4] to-[#e7f8f1] border-[#b7e7d5] hover:border-[#8fd2bb]",
    yellow:
      "from-[#fff8ea] to-[#fef4df] border-[#f1dcad] hover:border-[#e5c980]",
    red: "from-[#fff1f1] to-[#feeaea] border-[#f3c4c4] hover:border-[#e49b9b]",
  };

  const iconBgClasses = {
    blue: "bg-[#dbe8f7] text-[#2563eb]",
    green: "bg-[#d9f3e9] text-[#10b981]",
    yellow: "bg-[#f8ebc8] text-[#d97706]",
    red: "bg-[#f8dede] text-[#ef4444]",
  };

  const textColorClasses = {
    blue: "text-[#1d4ed8]",
    green: "text-[#059669]",
    yellow: "text-[#b45309]",
    red: "text-[#dc2626]",
  };

  const isDeltaPositive = delta !== null && delta >= 0;

  return (
    <div
      className={`bg-gradient-to-br ${colorClasses[color] || colorClasses.blue} border rounded-2xl p-6 shadow-md transition-all hover:shadow-lg`}
    >
      <div className="flex items-start justify-between">
        <div className="flex-1">
          <p className="text-[var(--text-muted)] text-sm font-medium uppercase tracking-wide">
            {title}
          </p>
          <div className="mt-3 flex items-baseline gap-2">
            <p
              className={`text-3xl md:text-4xl font-bold ${textColorClasses[color] || textColorClasses.blue}`}
            >
              {typeof value === "number"
                ? value.toLocaleString("en-IN", {
                    maximumFractionDigits: 1,
                  })
                : value || "—"}
            </p>
            {unit && (
              <p className="text-[var(--text-muted)] text-sm font-medium">
                {unit}
              </p>
            )}
          </div>
        </div>
        {Icon && (
          <div
            className={`${iconBgClasses[color] || iconBgClasses.blue} p-3 rounded-xl`}
          >
            <Icon size={28} strokeWidth={1.5} />
          </div>
        )}
      </div>

      {delta !== null && (
        <div className="mt-4 flex items-center gap-2 pt-3 border-t border-[var(--surface-border)]">
          {isDeltaPositive ? (
            <>
              <TrendingUp size={16} className="text-green-400" />
              <span className="text-green-400 text-sm font-medium">
                +{delta.toFixed(2)} {deltaLabel}
              </span>
            </>
          ) : (
            <>
              <TrendingDown size={16} className="text-red-400" />
              <span className="text-red-400 text-sm font-medium">
                {delta.toFixed(2)} {deltaLabel}
              </span>
            </>
          )}
        </div>
      )}
    </div>
  );
};
