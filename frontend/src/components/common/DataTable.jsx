import React, { useState } from "react";
import { ChevronUp, ChevronDown } from "lucide-react";

const COLUMN_LABELS = {
  // Date/Time/Day
  Date: "Date",
  Time: "Time",
  Day: "Day",

  // Backend-renamed columns (from processor.build_unified_dataframe)
  "Grid KWh": "Grid Energy Consumed (kWh)",
  "Solar KWh": "Solar Energy Generated (kWh)",
  "Total KWh": "Total Energy Consumed (kWh)",
  "Grid Cost (INR)": "Grid Energy Cost (INR)",
  "Diesel Cost (INR)": "Diesel Energy Cost (INR)",
  "Total Cost (INR)": "Total Energy Cost (INR)",
  "Energy Saving (INR)": "Energy Cost Savings (INR)",
  "Solar %": "Solar Contribution (%)",
  "Diesel consumed": "Diesel Fuel Consumed (Litres)",
  "Ambient Temp (°C)": "Ambient Temperature (°C)",
  "Inverter Status": "Inverter Status",

  // Solar-specific columns
  "Plant Capacity (KW)": "Plant Capacity (KW)",
  "Irradiance (W/m²)": "Irradiance (W/m²)",

  // Original CSV column names (for backwards compatibility)
  "Grid Units Consumed (KWh)": "Grid Energy Consumed (kWh)",
  "Total Units Consumed (KWh)": "Total Energy Consumed (kWh)",
  "DG Units Consumed (KWh)": "Diesel Generator Energy Consumed (kWh)",
  "Solar Units Generated (KWh)": "Solar Energy Generated (kWh)",
  "Generation (kWh)": "Solar Energy Generated (kWh)",
  "Total Units Consumed in INR": "Total Energy Cost (INR)",
  "Fuel Consumed (Litres)": "Diesel Fuel Consumed (Litres)",
  "DG Runtime (hrs)": "Diesel Generator Runtime (hrs)",
  "Avg Temp": "Ambient Temperature (°C)",
  "Ambient Temperature °C": "Ambient Temperature (°C)",
  "Energy Saving in INR": "Energy Cost Savings (INR)",
};

const getColumnLabel = (columnName) => {
  if (COLUMN_LABELS[columnName]) {
    return COLUMN_LABELS[columnName];
  }

  return String(columnName).replace(/_/g, " ").replace(/\s+/g, " ").trim();
};

export const DataTable = ({ data = [], columns = [], hideColumns = [] }) => {
  const [sortColumn, setSortColumn] = useState("Date");
  const [sortDirection, setSortDirection] = useState("desc");

  if (!data || data.length === 0) {
    return (
      <div className="text-center py-12 text-(--text-muted) text-lg">
        No data available
      </div>
    );
  }

  // Get columns to display - only show columns defined in COLUMN_LABELS
  const visibleColumns =
    columns.length > 0
      ? columns.filter(
          (col) => !hideColumns.includes(col) && COLUMN_LABELS[col],
        )
      : Object.keys(data[0]).filter(
          (key) => !hideColumns.includes(key) && COLUMN_LABELS[key],
        );

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
    <div className="overflow-x-auto border border-[var(--surface-border)] rounded-2xl bg-[var(--surface)] shadow-sm">
      <table className="w-full">
        <thead>
          <tr className="border-b border-white/10 bg-white/5">
            {visibleColumns.map((column) => (
              <th
                key={column}
                onClick={() => handleSort(column)}
                className="px-6 py-4 text-left text-xs font-bold text-[var(--text-muted)] cursor-pointer hover:bg-[var(--accent-100)]/60 select-none uppercase tracking-wide transition-colors"
              >
                <div className="flex items-center gap-2">
                  {getColumnLabel(column)}
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
              className={`border-b border-[var(--surface-border)] hover:bg-[var(--accent-100)]/55 transition-colors ${
                idx % 2 === 0 ? "bg-[var(--surface-soft)]" : ""
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
