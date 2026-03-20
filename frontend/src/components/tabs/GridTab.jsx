import React, { useState } from "react";
import { useDateStore } from "../../store/dateStore";
import { useGridKPIs, useGridData } from "../../hooks/useEnergyData";
import { KPICard } from "../common/KPICard";
import { DataTable } from "../common/DataTable";
import { ExportButton } from "../common/ExportButton";
import { StackedBarChart } from "../charts/StackedBarChart";
import { LoadingSpinner } from "../common/LoadingSpinner";
import { exportAPI } from "../../api/endpoints";
import { Zap, DollarSign, TrendingUp, AlertCircle } from "lucide-react";

export const GridTab = () => {
  const { startDate, endDate } = useDateStore();
  const [isExporting, setIsExporting] = useState(false);

  const {
    data: kpiData,
    isLoading: kpiLoading,
    error: kpiError,
  } = useGridKPIs(startDate, endDate);
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

  if (kpiLoading || dataLoading) {
    return <LoadingSpinner message="Loading grid data..." />;
  }

  if (kpiError || dataError) {
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

  const chartData =
    gridData?.data?.map((item) => ({
      Date: item.Date,
      "Grid Consumption": parseFloat(item["Grid Units Consumed (KWh)"]) || 0,
      "Total Consumption": parseFloat(item["Total Units Consumed (KWh)"]) || 0,
    })) || [];

  return (
    <div className="space-y-8">
      <div>
        <h2 className="text-2xl font-bold section-title mb-4">
          Grid Supply Metrics
        </h2>
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
          <KPICard
            title="Total Grid Energy"
            value={kpiData?.total_grid_kwh || 0}
            unit="kWh"
            color="blue"
            icon={Zap}
          />
          <KPICard
            title="Average Daily"
            value={kpiData?.avg_grid_kwh || 0}
            unit="kWh"
            color="blue"
          />
          <KPICard
            title="Peak Consumption"
            value={kpiData?.peak_grid_kwh || 0}
            unit="kWh"
            color="red"
            icon={TrendingUp}
          />
          <KPICard
            title="Total Cost"
            value={kpiData?.total_grid_cost || 0}
            unit="INR"
            color="red"
            icon={DollarSign}
          />
        </div>
      </div>

      <StackedBarChart
        data={chartData}
        title="Grid Energy Consumption"
        dataKeys={["Grid Consumption", "Total Consumption"]}
        colors={["#1f5ea8", "#5a6b7f"]}
      />

      <div>
        <div className="flex justify-between items-center mb-4">
          <h2 className="text-2xl font-bold section-title">
            Detailed Grid Data
          </h2>
          <ExportButton
            onClick={handleExport}
            isLoading={isExporting}
            label="Export Excel"
          />
        </div>
        <DataTable data={gridData?.data || []} hideColumns={[]} />
      </div>
    </div>
  );
};
