import { create } from "zustand";
import { format, subDays } from "date-fns";

// Initialize with last 30 days
const today = new Date();
const thirtyDaysAgo = subDays(today, 30);

const defaultStartDate = format(thirtyDaysAgo, "yyyy-MM-dd");
const defaultEndDate = format(today, "yyyy-MM-dd");

export const useDateStore = create((set) => ({
  startDate: defaultStartDate,
  endDate: defaultEndDate,

  setStartDate: (date) => set({ startDate: date }),
  setEndDate: (date) => set({ endDate: date }),
  setDateRange: (start, end) => set({ startDate: start, endDate: end }),
  resetDates: () =>
    set({ startDate: defaultStartDate, endDate: defaultEndDate }),
}));
