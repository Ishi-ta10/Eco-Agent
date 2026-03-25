import React from "react";
import { useDateStore } from "../../store/dateStore";
import { Calendar, RotateCcw } from "lucide-react";

export const DateRangeFilter = () => {
  const { startDate, endDate, setStartDate, setEndDate, resetDates } =
    useDateStore();

  return (
    <div className="flex gap-4 items-end flex-wrap">
      <div className="flex-1 min-w-[250px]">
        <label className="text-sm font-semibold text-[var(--text-muted)] uppercase tracking-wide mb-2 block">
          From Date
        </label>
        <div className="relative">
          <Calendar
            className="absolute left-3 top-3 text-[var(--accent-500)]"
            size={20}
          />
          <input
            type="date"
            value={startDate}
            onChange={(e) => setStartDate(e.target.value)}
            className="w-full pl-10 pr-4 py-2.5 bg-[var(--input-bg)] border border-[var(--input-border)] rounded-xl text-[var(--input-text)] placeholder-[var(--input-placeholder)] focus:outline-none focus:ring-2 focus:ring-[var(--accent-500)] focus:border-transparent transition-all"
          />
        </div>
      </div>

      <div className="text-[var(--text-muted)] text-xl">→</div>

      <div className="flex-1 min-w-[250px]">
        <label className="text-sm font-semibold text-[var(--text-muted)] uppercase tracking-wide mb-2 block">
          To Date
        </label>
        <div className="relative">
          <Calendar
            className="absolute left-3 top-3 text-[var(--accent-500)]"
            size={20}
          />
          <input
            type="date"
            value={endDate}
            onChange={(e) => setEndDate(e.target.value)}
            className="w-full pl-10 pr-4 py-2.5 bg-[var(--input-bg)] border border-[var(--input-border)] rounded-xl text-[var(--input-text)] placeholder-[var(--input-placeholder)] focus:outline-none focus:ring-2 focus:ring-[var(--accent-500)] focus:border-transparent transition-all"
          />
        </div>
      </div>

      <button onClick={resetDates} className="btn-primary">
        <RotateCcw size={16} />
        Reset
      </button>
    </div>
  );
};
