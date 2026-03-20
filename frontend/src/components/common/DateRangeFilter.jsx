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
            className="w-full pl-10 pr-4 py-2.5 bg-white/65 border border-[var(--surface-border)] rounded-xl text-[var(--text-primary)] placeholder-[var(--text-muted)] focus:outline-none focus:ring-2 focus:ring-[var(--accent-500)] focus:border-transparent transition-all"
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
            className="w-full pl-10 pr-4 py-2.5 bg-white/65 border border-[var(--surface-border)] rounded-xl text-[var(--text-primary)] placeholder-[var(--text-muted)] focus:outline-none focus:ring-2 focus:ring-[var(--accent-500)] focus:border-transparent transition-all"
          />
        </div>
      </div>

      <button
        onClick={resetDates}
        className="px-6 py-2.5 text-sm font-semibold text-white bg-[var(--accent-500)] rounded-xl hover:bg-[var(--accent-600)] transition-all flex items-center gap-2 shadow-md"
      >
        <RotateCcw size={16} />
        Reset
      </button>
    </div>
  );
};
