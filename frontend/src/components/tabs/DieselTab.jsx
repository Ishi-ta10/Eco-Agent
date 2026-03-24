import React, { useState } from "react";
import { useDateStore } from "../../store/dateStore";
import { useDieselKPIs, useDieselData } from "../../hooks/useEnergyData";
import { KPICard } from "../common/KPICard";
import { DataTable } from "../common/DataTable";
import { ExportButton } from "../common/ExportButton";
import { StackedBarChart } from "../charts/StackedBarChart";
import { LoadingSpinner } from "../common/LoadingSpinner";
import { exportAPI } from "../../api/endpoints";
import {
  Droplet,
  Clock,
  DollarSign,
  Zap,
  AlertCircle,
  Calendar,
} from "lucide-react";

export const DieselTab = () => {
  const { startDate, endDate } = useDateStore();
  const [isExporting, setIsExporting] = useState(false);

  const {
    data: kpiData,
    isLoading: kpiLoading,
    error: kpiError,
  } = useDieselKPIs(startDate, endDate);
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

  if (kpiLoading || dataLoading) {
    return <LoadingSpinner message="Loading diesel data..." />;
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
    dieselData?.data?.map((item) => ({
      Date: item.Date,
      "DG Consumption": parseFloat(item["DG Units Consumed (KWh)"]) || 0,
      "Diesel consumed":
        parseFloat(item["Diesel consumed"] ?? item["Fuel Consumed (Litres)"]) ||
        0,
    })) || [];

  const activeDieselData =
    dieselData?.data?.filter(
      (item) => (parseFloat(item["DG Units Consumed (KWh)"]) || 0) > 0,
    ) || [];

  return (
    <div className="space-y-8">
      <div>
        <h2 className="text-2xl font-bold section-title mb-4">
          Diesel Generator Metrics
        </h2>
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
          <KPICard
            title="Total DG Energy"
            value={kpiData?.total_diesel_kwh || 0}
            unit="kWh"
            color="red"
            icon={Zap}
          />
          <KPICard
            title="Total Runtime"
            value={kpiData?.total_runtime || 0}
            unit="hrs"
            color="red"
            icon={Clock}
          />
          <KPICard
            title="Diesel consumed"
            value={kpiData?.total_fuel || 0}
            unit="Liters"
            color="yellow"
            icon={Droplet}
          />
          <KPICard
            title="Total Cost"
            value={kpiData?.total_diesel_cost || 0}
            unit="INR"
            color="red"
            icon={DollarSign}
          />
        </div>
      </div>

      <StackedBarChart
        data={chartData}
        title="Diesel Generator Usage"
        dataKeys={["DG Consumption", "Diesel consumed"]}
        colors={["#b54747", "#d39b22"]}
      />

      <div className="rounded-2xl p-8 bg-gradient-to-br from-[#edf4fc] to-[#e6f0fb] border border-[#c2d8ee] shadow-md">
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
                out of {dieselData?.data?.length || 0} days
              </p>
            </div>
          </div>
          <div className="text-right">
            <p className="text-[var(--text-muted)] text-sm">Efficiency</p>
            <p className="text-2xl font-semibold text-[var(--accent-500)]">
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
            Detailed Diesel Data
          </h2>
          <ExportButton
            onClick={handleExport}
            isLoading={isExporting}
            label="Export Excel"
          />
        </div>
        <DataTable data={dieselData?.data || []} hideColumns={[]} />
      </div>
    </div>
  );
};
