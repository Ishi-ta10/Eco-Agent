import React, { useState } from "react";
import { useDieselData } from "../../hooks/useEnergyData";
import { KPICard } from "../common/KPICard";
import { DataTable } from "../common/DataTable";
import { ExportButton } from "../common/ExportButton";
import { StackedBarChart } from "../charts/StackedBarChart";
import { LoadingSpinner } from "../common/LoadingSpinner";
import { exportAPI } from "../../api/endpoints";
import {
  asNumber,
  EFFECTIVE_TODAY,
  EFFECTIVE_TODAY_DISPLAY,
  getLatestRow,
  getRecentDateRange,
  getRecentRows,
  getRowsForDate,
} from "../../utils/recentData";
import { Droplet, AlertCircle, Calendar } from "lucide-react";

export const DieselTab = () => {
  const [isExporting, setIsExporting] = useState(false);
  const { startDate, endDate } = getRecentDateRange(7);
  const {
    data: dieselData,
    isLoading: dataLoading,
    error: dataError,
  } = useDieselData(startDate, endDate);

  const handleExport = async () => {
    try {
      setIsExporting(true);
      const response = await exportAPI.exportDiesel(startDate, endDate);
      const url = window.URL.createObjectURL(new Blob([response.data]));
      const link = document.createElement("a");
      link.href = url;
      link.setAttribute(
        "download",
        `Diesel_Report_${new Date().toISOString().split("T")[0]}.xlsx`,
      );
      document.body.appendChild(link);
      link.click();
      link.parentElement.removeChild(link);
    } catch (error) {
      console.error("Export failed:", error);
      alert("Failed to export file");
    } finally {
      setIsExporting(false);
    }
  };

  if (dataLoading) {
    return <LoadingSpinner message="Loading diesel data..." />;
  }

  if (dataError) {
    return (
      <div className="text-center py-12">
        <AlertCircle
          className="mx-auto text-[var(--danger-600)] mb-3"
          size={32}
        />
        <p className="text-[var(--danger-600)] text-lg">Error loading data</p>
      </div>
    );
  }

  const recentDieselRows = getRecentRows(dieselData?.data || [], 7);
  const todayDieselRows = getRowsForDate(recentDieselRows, EFFECTIVE_TODAY);
  const latestDieselRow = getLatestRow(todayDieselRows);

  const latestDieselEnergyConsumed = asNumber(latestDieselRow, [
    "DG Units Consumed (KWh)",
    "Diesel KWh",
  ]);
  // Per requested UX, fuel-consumed visual mirrors DG energy values.
  const chartData =
    recentDieselRows?.map((item) => ({
      Date: item.Date,
      "Diesel Fuel Consumed": parseFloat(item["DG Units Consumed (KWh)"]) || 0,
    })) || [];

  const activeDieselData =
    recentDieselRows?.filter(
      (item) => (parseFloat(item["DG Units Consumed (KWh)"]) || 0) > 0,
    ) || [];

  return (
    <div className="space-y-8">
      <div>
        <h2 className="text-2xl font-bold section-title mb-4">
          Key Metrics of Today
        </h2>
        <p className="text-sm text-[var(--text-muted)] mb-4">
          Date: {EFFECTIVE_TODAY_DISPLAY}
        </p>
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
          <KPICard
            title="Diesel Fuel Consumed"
            value={latestDieselEnergyConsumed}
            unit="kWh"
            color="yellow"
            icon={Droplet}
          />
        </div>
      </div>

      <StackedBarChart
        data={chartData}
        title="Diesel Fuel Consumed (Last 7 Days)"
        dataKeys={["Diesel Fuel Consumed"]}
        colors={["#9f7b52"]}
      />

      <div className="rounded-2xl p-8 bg-gradient-to-br from-[#f2f6fb] to-[#e9f0f8] border border-[#c7d6e7] shadow-md">
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-4">
            <Calendar className="text-[var(--accent-500)]" size={32} />
            <div>
              <p className="text-[var(--text-muted)] text-sm uppercase tracking-wide">
                Active Generator Days
              </p>
              <p className="text-3xl font-bold text-[var(--text-primary)] mt-1">
                {activeDieselData.length}
              </p>
              <p className="text-[var(--text-muted)] text-sm mt-1">
                out of {recentDieselRows.length || 0} days
              </p>
            </div>
          </div>
          <div className="text-right">
            <p className="text-[var(--text-muted)] text-sm">Efficiency</p>
            <p className="text-2xl font-semibold text-[#3a5f88]">
              {(
                (activeDieselData.length / (dieselData?.data?.length || 1)) *
                100
              ).toFixed(1)}
              %
            </p>
          </div>
        </div>
      </div>

      <div>
        <div className="flex justify-between items-center mb-4">
          <h2 className="text-2xl font-bold section-title">
            Detailed Diesel Data (Last 7 Days)
          </h2>
          <ExportButton
            onClick={handleExport}
            isLoading={isExporting}
            label="Export Excel"
          />
        </div>
        <DataTable
          data={recentDieselRows}
          columns={[
            "Date",
            "Time",
            "Fuel Consumed (Litres)",
            "Total Cost (INR)",
          ]}
        />
      </div>
    </div>
  );
};
