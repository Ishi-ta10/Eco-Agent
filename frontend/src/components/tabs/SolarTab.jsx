import React, { useState } from "react";
import { useSolarData } from "../../hooks/useEnergyData";
import { KPICard } from "../common/KPICard";
import { DataTable } from "../common/DataTable";
import { ExportButton } from "../common/ExportButton";
import { StackedBarChart } from "../charts/StackedBarChart";
import { AreaChartComponent } from "../charts/AreaChart";
import { LoadingSpinner } from "../common/LoadingSpinner";
import { exportAPI } from "../../api/endpoints";
import {
  asNumber,
  countInverterFaults,
  EFFECTIVE_TODAY,
  EFFECTIVE_TODAY_DISPLAY,
  getLatestRow,
  getRecentDateRange,
  getRecentRows,
  getRowsForDate,
} from "../../utils/recentData";
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
          ? "bg-[#edf5f2] border-[#c0d8d0] hover:border-[#99bcae]"
          : "bg-[#f8eff1] border-[#debec4] hover:border-[#c99fa8]"
      }`}
    >
      <div className="flex items-center gap-3">
        <div
          className={`w-2 h-6 rounded-full ${isOnline ? "bg-gradient-to-b from-[#6fa791] to-[#437c65]" : "bg-gradient-to-b from-[#c17a86] to-[#9f5060]"}`}
        ></div>
        <div>
          <p className="font-semibold text-sm text-[var(--text-primary)]">
            {name}
          </p>
          <p
            className={`text-xs font-medium mt-1 ${isOnline ? "text-[#346f5a]" : "text-[#924857]"}`}
          >
            {isOnline ? "✓ Online" : "✗ Fault"}
          </p>
        </div>
      </div>
    </div>
  );
};

export const SolarTab = () => {
  const [isExporting, setIsExporting] = useState(false);
  const { startDate, endDate } = getRecentDateRange(7);
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

  if (dataLoading) {
    return <LoadingSpinner message="Loading solar data..." />;
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

  const recentSolarRows = getRecentRows(solarData?.data || [], 7);
  const todaySolarRows = getRowsForDate(recentSolarRows, EFFECTIVE_TODAY);
  const latestSolarRow = getLatestRow(todaySolarRows);
  const latestSolarEnergyGenerated = asNumber(latestSolarRow, [
    "Solar Units Generated (KWh)",
    "Solar KWh",
  ]);
  const smbValues = [
    "SMB1 (KWh)",
    "SMB2 (KWh)",
    "SMB3 (KWh)",
    "SMB4 (KWh)",
    "SMB5 (KWh)",
  ]
    .map((key) => asNumber(latestSolarRow, [key]))
    .filter((value) => value > 0);
  const latestAverageSmbOutput = smbValues.length
    ? smbValues.reduce((sum, value) => sum + value, 0) / smbValues.length
    : 0;
  const latestPeakSmbOutput = smbValues.length ? Math.max(...smbValues) : 0;
  // Calculate energy savings: Solar kWh * (grid_rate - solar_rate) = Solar kWh * 5.61
  const SAVINGS_RATE = 5.61; // Grid rate (7.11) - Solar rate (1.50)
  const latestEstimatedSavings = latestSolarEnergyGenerated * SAVINGS_RATE;
  const latestInverterFaultCount = countInverterFaults(
    latestSolarRow?.["Inverter Status"],
  );

  const smbs = ["SMB1", "SMB2", "SMB3", "SMB4", "SMB5"];
  const inverterStatuses = (() => {
    const records = recentSolarRows;
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
    recentSolarRows?.map((item) => ({
      Date: item.Date,
      "Solar Energy Generated (kWh)":
        parseFloat(item["Solar Units Generated (KWh)"]) || 0,
      "SMB1 Energy Generated (kWh)": parseFloat(item["SMB1 (KWh)"]) || 0,
      "SMB2 Energy Generated (kWh)": parseFloat(item["SMB2 (KWh)"]) || 0,
      "SMB3 Energy Generated (kWh)": parseFloat(item["SMB3 (KWh)"]) || 0,
      "SMB4 Energy Generated (kWh)": parseFloat(item["SMB4 (KWh)"]) || 0,
      "SMB5 Energy Generated (kWh)": parseFloat(item["SMB5 (KWh)"]) || 0,
    })) || [];

  const weeklyTrendData =
    recentSolarRows?.map((item) => ({
      Date: item?.Date,
      "Solar Energy Generated (kWh)":
        parseFloat(item?.["Solar Units Generated (KWh)"]) || 0,
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
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-5 gap-4">
          <KPICard
            title="Solar Energy Generated"
            value={latestSolarEnergyGenerated}
            unit="kWh"
            color="yellow"
            icon={Sun}
          />
          <KPICard
            title="Average SMB Output"
            value={latestAverageSmbOutput}
            unit="kWh"
            color="yellow"
          />
          <KPICard
            title="Peak SMB Output"
            value={latestPeakSmbOutput}
            unit="kWh"
            color="yellow"
            icon={TrendingUp}
          />
          <KPICard
            title="Estimated Energy Cost Savings"
            value={latestEstimatedSavings}
            unit="INR"
            color="green"
            icon={DollarSign}
          />
          <KPICard
            title="Inverter Fault Count"
            value={latestInverterFaultCount}
            unit="Count"
            color={latestInverterFaultCount > 0 ? "red" : "green"}
            icon={latestInverterFaultCount > 0 ? AlertCircle : CheckCircle2}
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

      <div className="w-full">
        <AreaChartComponent
          data={weeklyTrendData}
          title="Solar Energy Generation Trend (Last 7 Days)"
          dataKeys={["Solar Energy Generated (kWh)"]}
          colors={["#8f7a58"]}
        />
      </div>

      <div>
        <div className="flex justify-between items-center mb-4">
          <h2 className="text-2xl font-bold section-title">
            Detailed Solar Data (Last 7 Days)
          </h2>
          <ExportButton
            onClick={handleExport}
            isLoading={isExporting}
            label="Export Excel"
          />
        </div>
        <DataTable
          data={recentSolarRows}
          columns={[
            "Date",
            "Day",
            "Time",
            "Solar Units Generated (KWh)",
            "Inverter Status",
          ]}
        />
      </div>
    </div>
  );
};
