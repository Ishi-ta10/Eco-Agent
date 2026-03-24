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
  const formattedValue =
    typeof value === "number"
      ? value.toLocaleString("en-IN", {
          maximumFractionDigits: 1,
        })
      : value || "—";

  return (
    <div
      className={`bg-gradient-to-br ${colorClasses[color] || colorClasses.blue} border rounded-2xl p-6 shadow-md transition-all hover:shadow-lg h-full overflow-hidden`}
    >
      <div className="flex items-start justify-between gap-3 min-h-[56px]">
        <p className="text-[var(--text-muted)] text-sm font-medium uppercase tracking-wide leading-6">
          {title}
        </p>

        <div
          className={`${iconBgClasses[color] || iconBgClasses.blue} p-3 rounded-xl shrink-0 ${Icon ? "opacity-100" : "opacity-0"}`}
          aria-hidden={!Icon}
        >
          {Icon ? (
            <Icon size={28} strokeWidth={1.5} />
          ) : (
            <span className="block w-7 h-7" />
          )}
        </div>
      </div>

      <div className="mt-4 flex items-end gap-2 min-h-[64px]">
        <p
          className={`text-[clamp(2rem,2.8vw,3.1rem)] leading-none tracking-tight font-bold break-words ${textColorClasses[color] || textColorClasses.blue}`}
        >
          {formattedValue}
        </p>
        {unit && (
          <p className="text-[var(--text-muted)] text-sm font-medium whitespace-nowrap pb-1">
            {unit}
          </p>
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
