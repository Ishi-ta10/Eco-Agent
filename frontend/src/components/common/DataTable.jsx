import React, { useState } from "react";
import { ChevronUp, ChevronDown } from "lucide-react";

export const DataTable = ({ data = [], columns = [], hideColumns = [] }) => {
  const [sortColumn, setSortColumn] = useState(null);
  const [sortDirection, setSortDirection] = useState("asc");

  if (!data || data.length === 0) {
    return (
      <div className="text-center py-12 text-[var(--text-muted)] text-lg">
        No data available
      </div>
    );
  }

  // Get columns to display
  const visibleColumns =
    columns.length > 0
      ? columns.filter((col) => !hideColumns.includes(col))
      : Object.keys(data[0]).filter((key) => !hideColumns.includes(key));

  // Sort data
  let sortedData = [...data];
  if (sortColumn) {
    sortedData.sort((a, b) => {
      const aVal = a[sortColumn];
      const bVal = b[sortColumn];

      if (typeof aVal === "number" && typeof bVal === "number") {
        return sortDirection === "asc" ? aVal - bVal : bVal - aVal;
      }

      const aStr = String(aVal).toLowerCase();
      const bStr = String(bVal).toLowerCase();
      return sortDirection === "asc"
        ? aStr.localeCompare(bStr)
        : bStr.localeCompare(aStr);
    });
  }

  const handleSort = (column) => {
    if (sortColumn === column) {
      setSortDirection(sortDirection === "asc" ? "desc" : "asc");
    } else {
      setSortColumn(column);
      setSortDirection("asc");
    }
  };

  return (
    <div className="overflow-x-auto border border-[var(--surface-border)] rounded-2xl bg-[var(--surface)]">
      <table className="w-full">
        <thead>
          <tr className="border-b border-white/10 bg-white/5">
            {visibleColumns.map((column) => (
              <th
                key={column}
                onClick={() => handleSort(column)}
                className="px-6 py-4 text-left text-xs font-bold text-[var(--text-muted)] cursor-pointer hover:bg-[var(--accent-100)] select-none uppercase tracking-wide transition-colors"
              >
                <div className="flex items-center gap-2">
                  {column}
                  {sortColumn === column &&
                    (sortDirection === "asc" ? (
                      <ChevronUp
                        size={14}
                        className="text-[var(--accent-500)]"
                      />
                    ) : (
                      <ChevronDown
                        size={14}
                        className="text-[var(--accent-500)]"
                      />
                    ))}
                </div>
              </th>
            ))}
          </tr>
        </thead>
        <tbody>
          {sortedData.map((row, idx) => (
            <tr
              key={idx}
              className={`border-b border-[var(--surface-border)] hover:bg-[var(--accent-100)] transition-colors ${
                idx % 2 === 0 ? "bg-white/30" : ""
              }`}
            >
              {visibleColumns.map((column) => (
                <td
                  key={column}
                  className="px-6 py-4 text-sm text-[var(--text-primary)]"
                >
                  {typeof row[column] === "number"
                    ? row[column].toLocaleString("en-IN", {
                        maximumFractionDigits: 2,
                      })
                    : String(row[column])}
                </td>
              ))}
            </tr>
          ))}
        </tbody>
      </table>
      <div className="px-6 py-4 bg-[var(--surface-soft)] border-t border-[var(--surface-border)] text-sm text-[var(--text-muted)] font-medium">
        Showing {sortedData.length} records
      </div>
    </div>
  );
};
