import { create } from "zustand";
import { format, subDays } from "date-fns";
import { EFFECTIVE_TODAY } from "../utils/recentData";

// Initialize with last 7 days
const today = new Date(`${EFFECTIVE_TODAY}T00:00:00`);
const sevenDaysAgo = subDays(today, 6);

const defaultStartDate = format(sevenDaysAgo, "yyyy-MM-dd");
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
