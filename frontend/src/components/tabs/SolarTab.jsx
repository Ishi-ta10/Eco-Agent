import React, { useState } from "react";
import { useDateStore } from "../../store/dateStore";
import { useSolarKPIs, useSolarData } from "../../hooks/useEnergyData";
import { KPICard } from "../common/KPICard";
import { DataTable } from "../common/DataTable";
import { ExportButton } from "../common/ExportButton";
import { StackedBarChart } from "../charts/StackedBarChart";
import { AreaChartComponent } from "../charts/AreaChart";
import { LoadingSpinner } from "../common/LoadingSpinner";
import { exportAPI } from "../../api/endpoints";
import {
  Sun,
  DollarSign,
  TrendingUp,
  Zap,
  AlertCircle,
  CheckCircle2,
} from "lucide-react";

const InverterStatus = ({ name, status }) => {
  const isOnline = status === "All Online";
  return (
    <div
      className={`p-4 rounded-xl border transition-all ${
        isOnline
          ? "bg-[#ebf7f2] border-[#b8ddcd] hover:border-[#95c8b3]"
          : "bg-[#fcf0ef] border-[#e4c2bf] hover:border-[#cf9f99]"
      }`}
    >
      <div className="flex items-center gap-3">
        <div
          className={`w-2 h-6 rounded-full ${isOnline ? "bg-gradient-to-b from-green-400 to-green-600" : "bg-gradient-to-b from-red-400 to-red-600"}`}
        ></div>
        <div>
          <p className="font-semibold text-sm text-[var(--text-primary)]">
            {name}
          </p>
          <p
            className={`text-xs font-medium mt-1 ${isOnline ? "text-[#1b7f5b]" : "text-[#b54747]"}`}
          >
            {isOnline ? "✓ Online" : "✗ Fault"}
          </p>
        </div>
      </div>
    </div>
  );
};

export const SolarTab = () => {
  const { startDate, endDate } = useDateStore();
  const [isExporting, setIsExporting] = useState(false);

  const {
    data: kpiData,
    isLoading: kpiLoading,
    error: kpiError,
  } = useSolarKPIs(startDate, endDate);
  const {
    data: solarData,
    isLoading: dataLoading,
    error: dataError,
  } = useSolarData(startDate, endDate);

  const handleExport = async () => {
    try {
      setIsExporting(true);
      const response = await exportAPI.exportSolar(startDate, endDate);
      const url = window.URL.createObjectURL(new Blob([response.data]));
      const link = document.createElement("a");
      link.href = url;
      link.setAttribute(
        "download",
        `Solar_Report_${new Date().toISOString().split("T")[0]}.xlsx`,
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
    return <LoadingSpinner message="Loading solar data..." />;
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

  const smbs = ["SMB1", "SMB2", "SMB3", "SMB4", "SMB5"];
  const inverterStatuses = (() => {
    const records = solarData?.data || [];
    const defaultStatuses = smbs.reduce((acc, smb) => {
      acc[smb] = { name: smb, status: "All Online" };
      return acc;
    }, {});

    if (!records.length) return defaultStatuses;

    const sorted = [...records].sort((a, b) => {
      const aKey = `${a.Date || ""} ${a.Time || ""}`;
      const bKey = `${b.Date || ""} ${b.Time || ""}`;
      return bKey.localeCompare(aKey);
    });

    const latestWithStatus = sorted.find(
      (item) =>
        item["Inverter Status"] && String(item["Inverter Status"]).trim(),
    );
    if (!latestWithStatus) return defaultStatuses;

    const rawStatus = String(latestWithStatus["Inverter Status"]).trim();
    const normalized = rawStatus.toLowerCase();

    if (normalized === "all online") {
      return defaultStatuses;
    }

    const statuses = smbs.reduce((acc, smb) => {
      acc[smb] = { name: smb, status: "All Online" };
      return acc;
    }, {});

    if (normalized.includes("fault")) {
      let matchedAny = false;
      smbs.forEach((smb) => {
        if (normalized.includes(smb.toLowerCase())) {
          statuses[smb].status = `${smb} Fault`;
          matchedAny = true;
        }
      });

      if (!matchedAny) {
        smbs.forEach((smb) => {
          statuses[smb].status = "Fault";
        });
      }
    }

    return statuses;
  })();

  const smbChartData =
    solarData?.data?.map((item) => ({
      Date: item.Date,
      "Solar Generated": parseFloat(item["Solar Units Generated (KWh)"]) || 0,
      SMB1: parseFloat(item["SMB1 (KWh)"]) || 0,
      SMB2: parseFloat(item["SMB2 (KWh)"]) || 0,
      SMB3: parseFloat(item["SMB3 (KWh)"]) || 0,
      SMB4: parseFloat(item["SMB4 (KWh)"]) || 0,
      SMB5: parseFloat(item["SMB5 (KWh)"]) || 0,
    })) || [];

  const weeklyTrendData =
    kpiData?.weekly_trend?.map((item) => ({
      Date: item?.Day
        ? `${item.Day.slice(0, 3)} (${item.Date.slice(5)})`
        : item.Date,
      "Solar Generated": parseFloat(item?.Generation) || 0,
    })) || [];

  return (
    <div className="space-y-8">
      <div>
        <h2 className="text-2xl font-bold section-title mb-4">
          Solar Panel Metrics
        </h2>
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-5 gap-4">
          <KPICard
            title="Total Solar"
            value={kpiData?.total_solar_kwh || 0}
            unit="kWh"
            color="yellow"
            icon={Sun}
          />
          <KPICard
            title="Average Daily"
            value={kpiData?.avg_solar_kwh || 0}
            unit="kWh"
            color="yellow"
          />
          <KPICard
            title="Peak Generation"
            value={kpiData?.peak_solar_kwh || 0}
            unit="kWh"
            color="yellow"
            icon={TrendingUp}
          />
          <KPICard
            title="Energy Saved"
            value={kpiData?.energy_saved || 0}
            unit="INR"
            color="green"
            icon={DollarSign}
          />
          <KPICard
            title="Inverter Faults"
            value={kpiData?.inverter_faults || 0}
            unit="Count"
            color={kpiData?.inverter_faults > 0 ? "red" : "green"}
            icon={kpiData?.inverter_faults > 0 ? AlertCircle : CheckCircle2}
          />
        </div>
      </div>

      <div className="surface-card rounded-2xl p-8">
        <h2 className="text-2xl font-bold section-title mb-6 flex items-center gap-2">
          <Zap className="text-[var(--accent-500)]" size={28} />
          Inverter Status
        </h2>
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-5 gap-4">
          {Object.values(inverterStatuses).map((inverter, idx) => (
            <InverterStatus
              key={idx}
              name={inverter.name}
              status={inverter.status}
            />
          ))}
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <AreaChartComponent
          data={weeklyTrendData}
          title="Solar Generation Trend (Last 7 Days)"
          dataKeys={["Solar Generated"]}
          colors={["#d39b22"]}
        />
        <StackedBarChart
          data={smbChartData}
          title="SMB Contribution"
          dataKeys={["SMB1", "SMB2", "SMB3", "SMB4", "SMB5"]}
          colors={["#1f5ea8", "#c57c22", "#1b7f5b", "#b54747", "#5a6b7f"]}
        />
      </div>

      <div>
        <div className="flex justify-between items-center mb-4">
          <h2 className="text-2xl font-bold section-title">
            Detailed Solar Data
          </h2>
          <ExportButton
            onClick={handleExport}
            isLoading={isExporting}
            label="Export Excel"
          />
        </div>
        <DataTable
          data={solarData?.data || []}
          hideColumns={["Irradiance (W/m²)"]}
        />
      </div>
    </div>
  );
};
