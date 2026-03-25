import React, { useState } from "react";
import { useGridData } from "../../hooks/useEnergyData";
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
import { Zap, DollarSign, TrendingUp, AlertCircle } from "lucide-react";

export const GridTab = () => {
  const [isExporting, setIsExporting] = useState(false);
  const { startDate, endDate } = getRecentDateRange(7);
  const {
    data: gridData,
    isLoading: dataLoading,
    error: dataError,
  } = useGridData(startDate, endDate);

  const handleExport = async () => {
    try {
      setIsExporting(true);
      const response = await exportAPI.exportGrid(startDate, endDate);
      const url = window.URL.createObjectURL(new Blob([response.data]));
      const link = document.createElement("a");
      link.href = url;
      link.setAttribute(
        "download",
        `Grid_Report_${new Date().toISOString().split("T")[0]}.xlsx`,
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
    return <LoadingSpinner message="Loading grid data..." />;
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

  const recentGridRows = getRecentRows(gridData?.data || [], 7);
  const todayGridRows = getRowsForDate(recentGridRows, EFFECTIVE_TODAY);
  const latestGridRow = getLatestRow(todayGridRows);

  const latestGridEnergyConsumed = asNumber(latestGridRow, [
    "Grid Units Consumed (KWh)",
    "Grid KWh",
  ]);
  const latestTotalEnergyConsumed = asNumber(latestGridRow, [
    "Total Units Consumed (KWh)",
    "Total KWh",
  ]);
  const latestGridEnergyCost = asNumber(latestGridRow, [
    "Total Units Consumed in INR",
    "Grid Cost (INR)",
    "Grid Cost",
    "Cost (INR)",
    "Cost",
  ]);
  const latestGridContribution = latestTotalEnergyConsumed
    ? (latestGridEnergyConsumed / latestTotalEnergyConsumed) * 100
    : 0;

  const chartData =
    recentGridRows?.map((item) => ({
      Date: item.Date,
      "Grid Energy Consumed (kWh)":
        asNumber(item, ["Grid Units Consumed (KWh)", "Grid KWh"]),
      "Total Energy Consumed (kWh)":
        asNumber(item, ["Total Units Consumed (KWh)", "Total KWh"]),
    })) || [];

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
            title="Grid Energy Consumed"
            value={latestGridEnergyConsumed}
            unit="kWh"
            color="blue"
            icon={Zap}
          />
          <KPICard
            title="Total Energy Consumed"
            value={latestTotalEnergyConsumed}
            unit="kWh"
            color="blue"
          />
          <KPICard
            title="Grid Contribution To Consumption"
            value={latestGridContribution}
            unit="%"
            color="red"
            icon={TrendingUp}
          />
          <KPICard
            title="Grid Energy Cost"
            value={latestGridEnergyCost}
            unit="INR"
            color="red"
            icon={DollarSign}
          />
        </div>
      </div>

      <StackedBarChart
        data={chartData}
        title="Grid Energy Consumption (Last 7 Days)"
        dataKeys={["Grid Energy Consumed (kWh)", "Total Energy Consumed (kWh)"]}
        colors={["#496e97", "#6e8093"]}
      />

      <div>
        <div className="flex justify-between items-center mb-4">
          <h2 className="text-2xl font-bold section-title">
            Detailed Grid Data (Last 7 Days)
          </h2>
          <ExportButton
            onClick={handleExport}
            isLoading={isExporting}
            label="Export Excel"
          />
        </div>
        <DataTable
          data={recentGridRows}
          columns={[
            "Date",
            "Day",
            "Time",
            "Ambient Temperature °C",
            "Grid Units Consumed (KWh)",
            "Total Units Consumed (KWh)",
            "Total Units Consumed in INR",
            "Energy Saving in INR",
          ]}
        />
      </div>
    </div>
  );
};
