import React, { useMemo, useState } from "react";
import {
  format,
  startOfMonth,
  subDays,
  differenceInCalendarDays,
  parseISO,
} from "date-fns";
import {
  CalendarRange,
  CheckCircle2,
  Pin,
  PinOff,
  SlidersHorizontal,
  ToggleLeft,
  ToggleRight,
} from "lucide-react";
import { DateRangeFilter } from "../common/DateRangeFilter";
import { useDateStore } from "../../store/dateStore";
import { useTabStore } from "../../store/tabStore";

const PRESET_OPTIONS = [
  {
    id: "last-7",
    label: "Last 7 Days",
    getRange: () => {
      const end = new Date();
      const start = subDays(end, 6);
      return {
        start: format(start, "yyyy-MM-dd"),
        end: format(end, "yyyy-MM-dd"),
      };
    },
  },
  {
    id: "last-30",
    label: "Last 30 Days",
    getRange: () => {
      const end = new Date();
      const start = subDays(end, 29);
      return {
        start: format(start, "yyyy-MM-dd"),
        end: format(end, "yyyy-MM-dd"),
      };
    },
  },
  {
    id: "month-to-date",
    label: "Month To Date",
    getRange: () => {
      const end = new Date();
      const start = startOfMonth(end);
      return {
        start: format(start, "yyyy-MM-dd"),
        end: format(end, "yyyy-MM-dd"),
      };
    },
  },
];

export const FiltersTab = () => {
  const { startDate, endDate, setDateRange } = useDateStore();
  const { setActiveTab } = useTabStore();
  const [isCompareEnabled, setIsCompareEnabled] = useState(false);
  const [isPinned, setIsPinned] = useState(false);

  const rangeHealth = useMemo(() => {
    if (!startDate || !endDate) {
      return {
        valid: false,
        days: 0,
        message: "Select a complete date range.",
      };
    }

    const start = parseISO(startDate);
    const end = parseISO(endDate);

    if (Number.isNaN(start.getTime()) || Number.isNaN(end.getTime())) {
      return {
        valid: false,
        days: 0,
        message: "Dates are invalid. Please reselect.",
      };
    }

    if (start > end) {
      return {
        valid: false,
        days: 0,
        message: "From Date cannot be later than To Date.",
      };
    }

    const totalDays = differenceInCalendarDays(end, start) + 1;

    return {
      valid: true,
      days: totalDays,
      message: `Range selected: ${totalDays} day${totalDays > 1 ? "s" : ""}`,
    };
  }, [startDate, endDate]);

  const applyPreset = (preset) => {
    const range = preset.getRange();
    setDateRange(range.start, range.end);
  };

  return (
    <div className="space-y-6 fade-in-up">
      <div className="surface-card rounded-2xl p-6">
        <h2 className="text-2xl font-bold section-title mb-2 flex items-center gap-2">
          <SlidersHorizontal className="text-[var(--accent-500)]" size={24} />
          Date Filters Workspace
        </h2>
        <p className="text-[var(--text-muted)]">
          Configure reporting windows and apply reusable filter presets across
          the dashboard.
        </p>
      </div>

      <div className="grid grid-cols-1 xl:grid-cols-3 gap-6">
        <div className="xl:col-span-2 surface-card rounded-2xl p-6">
          <h3 className="text-lg font-semibold section-title mb-4 flex items-center gap-2">
            <CalendarRange className="text-[var(--accent-500)]" size={20} />
            Primary Date Window
          </h3>
          <DateRangeFilter />

          <div className="mt-5">
            <p className="text-xs uppercase tracking-wide text-[var(--text-muted)] mb-2">
              Quick Presets
            </p>
            <div className="flex flex-wrap gap-2">
              {PRESET_OPTIONS.map((preset) => (
                <button
                  key={preset.id}
                  type="button"
                  onClick={() => applyPreset(preset)}
                  className="px-4 py-2 rounded-xl border border-[var(--surface-border)] bg-[var(--surface-soft)] text-[var(--text-primary)] font-semibold text-sm hover:bg-[var(--accent-100)] transition-colors"
                >
                  {preset.label}
                </button>
              ))}
            </div>
          </div>
        </div>

        <div className="surface-card rounded-2xl p-6">
          <h3 className="text-lg font-semibold section-title mb-4">
            Filter Intelligence
          </h3>
          <div
            className={`rounded-xl p-4 border ${
              rangeHealth.valid
                ? "bg-[#edf5f2] border-[#c0d8d0]"
                : "bg-[#f8eff1] border-[#debec4]"
            }`}
          >
            <p
              className={
                rangeHealth.valid ? "text-[#346f5a]" : "text-[#924857]"
              }
            >
              {rangeHealth.message}
            </p>
          </div>

          <div className="mt-4 space-y-3">
            <button
              type="button"
              onClick={() => setIsCompareEnabled((state) => !state)}
              className="w-full flex items-center justify-between rounded-xl border border-[var(--surface-border)] px-4 py-3 bg-[var(--surface-soft)] hover:bg-[var(--accent-100)] transition-colors"
            >
              <span className="text-sm font-semibold text-[var(--text-primary)]">
                Compare With Previous Period
              </span>
              {isCompareEnabled ? (
                <ToggleRight className="text-[var(--accent-500)]" size={20} />
              ) : (
                <ToggleLeft className="text-[var(--text-muted)]" size={20} />
              )}
            </button>

            <button
              type="button"
              onClick={() => setIsPinned((state) => !state)}
              className="w-full flex items-center justify-between rounded-xl border border-[var(--surface-border)] px-4 py-3 bg-[var(--surface-soft)] hover:bg-[var(--accent-100)] transition-colors"
            >
              <span className="text-sm font-semibold text-[var(--text-primary)]">
                Pin Filters For This Session
              </span>
              {isPinned ? (
                <Pin className="text-[var(--accent-500)]" size={18} />
              ) : (
                <PinOff className="text-[var(--text-muted)]" size={18} />
              )}
            </button>
          </div>

          <button
            type="button"
            onClick={() => setActiveTab("overview")}
            className="btn-primary w-full justify-center mt-5"
            disabled={!rangeHealth.valid}
          >
            <CheckCircle2 size={16} />
            Apply And Open Overview
          </button>
        </div>
      </div>
    </div>
  );
};
