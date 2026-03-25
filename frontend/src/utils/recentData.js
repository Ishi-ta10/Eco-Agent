import { format, subDays } from "date-fns";

export const EFFECTIVE_TODAY = "2026-03-22";
export const EFFECTIVE_TODAY_DISPLAY = "22-03-2026";

const normalizeDateString = (value) => {
  if (!value) return "";

  const text = String(value).trim();

  const ymdMatch = text.match(/^(\d{4})-(\d{2})-(\d{2})$/);
  if (ymdMatch) {
    return `${ymdMatch[1]}-${ymdMatch[2]}-${ymdMatch[3]}`;
  }

  const dmyMatch = text.match(/^(\d{2})-(\d{2})-(\d{4})$/);
  if (dmyMatch) {
    return `${dmyMatch[3]}-${dmyMatch[2]}-${dmyMatch[1]}`;
  }

  const parsed = new Date(text);
  if (!Number.isNaN(parsed.getTime())) {
    return format(parsed, "yyyy-MM-dd");
  }

  return text;
};

const getTimestamp = (row = {}) => {
  const dateValue = row?.Date || row?.date;
  if (!dateValue) return Number.NEGATIVE_INFINITY;

  const timeValue = row?.Time || row?.time || "00:00:00";
  const parsed = new Date(`${dateValue}T${timeValue}`);
  const time = parsed.getTime();

  if (Number.isNaN(time)) {
    const fallback = new Date(dateValue).getTime();
    return Number.isNaN(fallback) ? Number.NEGATIVE_INFINITY : fallback;
  }

  return time;
};

export const getRecentDateRange = (days = 7) => {
  const end = new Date(`${EFFECTIVE_TODAY}T00:00:00`);
  const start = subDays(end, Math.max(days - 1, 0));
  return {
    startDate: format(start, "yyyy-MM-dd"),
    endDate: format(end, "yyyy-MM-dd"),
  };
};

export const asNumber = (row, keys) => {
  for (const key of keys) {
    const value = row?.[key];
    if (value !== undefined && value !== null && value !== "") {
      const parsed = parseFloat(value);
      if (!Number.isNaN(parsed)) {
        return parsed;
      }
    }
  }
  return 0;
};

export const getRecentRows = (rows = [], maxDays = 7) => {
  if (!Array.isArray(rows) || rows.length === 0) {
    return [];
  }

  const sortedDesc = [...rows].sort(
    (a, b) => getTimestamp(b) - getTimestamp(a),
  );
  const recentDates = [];

  for (const row of sortedDesc) {
    const date = row?.Date || row?.date;
    if (!date) continue;
    if (!recentDates.includes(date)) {
      recentDates.push(date);
    }
    if (recentDates.length >= maxDays) {
      break;
    }
  }

  if (recentDates.length === 0) {
    return [];
  }

  return sortedDesc
    .filter((row) => recentDates.includes(row?.Date || row?.date))
    .sort((a, b) => getTimestamp(a) - getTimestamp(b));
};

export const getLatestRow = (rows = []) => {
  if (!Array.isArray(rows) || rows.length === 0) {
    return null;
  }

  return [...rows].sort((a, b) => getTimestamp(b) - getTimestamp(a))[0] || null;
};

export const getRowsForDate = (rows = [], targetDate = EFFECTIVE_TODAY) => {
  if (!Array.isArray(rows) || rows.length === 0) {
    return [];
  }

  const normalizedTargetDate = normalizeDateString(targetDate);
  if (!normalizedTargetDate) {
    return [];
  }

  return rows
    .filter((row) => {
      const rowDate = row?.Date || row?.date;
      return normalizeDateString(rowDate) === normalizedTargetDate;
    })
    .sort((a, b) => getTimestamp(a) - getTimestamp(b));
};

export const countInverterFaults = (statusText = "") => {
  const normalized = String(statusText).toLowerCase();
  if (!normalized || normalized === "all online") {
    return 0;
  }

  if (!normalized.includes("fault")) {
    return 0;
  }

  const smbMatches = normalized.match(/smb\s*\d+/g);
  if (smbMatches && smbMatches.length > 0) {
    return new Set(smbMatches.map((item) => item.replace(/\s+/g, ""))).size;
  }

  return 1;
};
