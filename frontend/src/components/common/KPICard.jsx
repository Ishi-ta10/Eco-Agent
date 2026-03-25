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
    blue: "from-[#f2f6fb] to-[#e9f0f8] border-[#c7d6e7] hover:border-[#9fb6d0]",
    green:
      "from-[#eff7f4] to-[#e7f1ed] border-[#bfd9cf] hover:border-[#98c2b2]",
    yellow:
      "from-[#faf6ef] to-[#f4efe4] border-[#ddcfb6] hover:border-[#c8b492]",
    red: "from-[#fbf1f2] to-[#f6e9ea] border-[#e2c0c5] hover:border-[#cb9ea6]",
  };

  const iconBgClasses = {
    blue: "bg-[#d8e4f2] text-[#335d88]",
    green: "bg-[#dcece6] text-[#3a7361]",
    yellow: "bg-[#ece3cf] text-[#957349]",
    red: "bg-[#eedcdf] text-[#9d5260]",
  };

  const textColorClasses = {
    blue: "text-[#294b6d]",
    green: "text-[#2e6756]",
    yellow: "text-[#7f6542]",
    red: "text-[#954957]",
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
              <TrendingUp size={16} className="text-[var(--success-600)]" />
              <span className="text-[var(--success-600)] text-sm font-medium">
                +{delta.toFixed(2)} {deltaLabel}
              </span>
            </>
          ) : (
            <>
              <TrendingDown size={16} className="text-[var(--danger-600)]" />
              <span className="text-[var(--danger-600)] text-sm font-medium">
                {delta.toFixed(2)} {deltaLabel}
              </span>
            </>
          )}
        </div>
      )}
    </div>
  );
};
