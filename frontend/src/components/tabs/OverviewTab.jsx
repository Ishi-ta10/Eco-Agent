import React, { useState } from "react";
import { useDateStore } from "../../store/dateStore";
import {
  useOverviewKPIs,
  useSolarData,
  useUnifiedData,
} from "../../hooks/useEnergyData";
import { KPICard } from "../common/KPICard";
import { DataTable } from "../common/DataTable";
import { ExportButton } from "../common/ExportButton";
import { StackedBarChart } from "../charts/StackedBarChart";
import { LineChartComponent } from "../charts/LineChart";
import { DonutChart } from "../charts/DonutChart";
import { LoadingSpinner } from "../common/LoadingSpinner";
import { exportAPI } from "../../api/endpoints";
import {
  Zap,
  Sun,
  DollarSign,
  Leaf,
  Thermometer,
  TrendingUp,
  ShieldCheck,
  CircleDollarSign,
} from "lucide-react";

const asNumber = (row, keys) => {
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

const buildOverviewChartData = (rows = []) => {
  const groupedByDate = rows.reduce((acc, row) => {
    const date = row?.Date || "Unknown";
    if (!acc[date]) {
      acc[date] = { Date: date, Grid: 0, Solar: 0, Diesel: 0 };
    }

    acc[date].Grid += asNumber(row, ["Grid KWh", "Grid Units Consumed (KWh)"]);
    acc[date].Solar += asNumber(row, [
      "Solar KWh",
      "Solar Units Generated (KWh)",
    ]);
    acc[date].Diesel += asNumber(row, [
      "Diesel KWh",
      "DG Units Consumed (KWh)",
    ]);
    return acc;
  }, {});

  return Object.values(groupedByDate).sort((a, b) =>
    String(a.Date).localeCompare(String(b.Date)),
  );
};

export const OverviewTab = () => {
  const { startDate, endDate } = useDateStore();
  const [isExporting, setIsExporting] = useState(false);

  const {
    data: kpiData,
    isLoading: kpiLoading,
    error: kpiError,
  } = useOverviewKPIs(startDate, endDate);
  const {
    data: unifiedData,
    isLoading: dataLoading,
    error: dataError,
  } = useUnifiedData(startDate, endDate);
  const {
    data: solarData,
    isLoading: solarLoading,
    error: solarError,
  } = useSolarData(startDate, endDate);
  const {
    data: fallbackSolarData,
    isLoading: fallbackSolarLoading,
    error: fallbackSolarError,
  } = useSolarData();

  const handleExport = async () => {
    try {
      setIsExporting(true);
      const response = await exportAPI.exportUnified(startDate, endDate);
      const url = window.URL.createObjectURL(new Blob([response.data]));
      const link = document.createElement("a");
      link.href = url;
      link.setAttribute(
        "download",
        `Unified_Report_${new Date().toISOString().split("T")[0]}.xlsx`,
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

  if (kpiLoading || dataLoading || solarLoading || fallbackSolarLoading) {
    return <LoadingSpinner message="Loading overview data..." />;
  }

  if (kpiError || dataError || solarError || fallbackSolarError) {
    return (
      <div className="text-center py-12">
        <p className="text-[var(--danger-600)] text-lg">
          Error loading data. Please check backend connection.
        </p>
        <p className="text-[var(--text-muted)] mt-2">
          {kpiError?.message || dataError?.message}
        </p>
      </div>
    );
  }

  const selectedSolarRows = solarData?.data || [];
  const fallbackSolarRows = fallbackSolarData?.data || [];
  const useSolarFallback =
    selectedSolarRows.length === 0 && fallbackSolarRows.length > 0;
  const activeSolarRows = useSolarFallback
    ? fallbackSolarRows
    : selectedSolarRows;
  const activeSolarRange = useSolarFallback
    ? fallbackSolarData?.date_range
    : solarData?.date_range;

  const chartData = buildOverviewChartData(unifiedData?.data || []);
  const totalGrid = chartData.reduce((sum, row) => sum + row.Grid, 0);
  const rangeSolarTotal = chartData.reduce((sum, row) => sum + row.Solar, 0);
  const fallbackSolarTotal = activeSolarRows.reduce(
    (sum, row) =>
      sum + asNumber(row, ["Solar Units Generated (KWh)", "Solar KWh"]),
    0,
  );
  const totalSolar = rangeSolarTotal > 0 ? rangeSolarTotal : fallbackSolarTotal;
  const totalDiesel = chartData.reduce((sum, row) => sum + row.Diesel, 0);
  const combinedTotal = totalGrid + totalSolar + totalDiesel;

  const sourceMixData = [
    {
      name: "Grid",
      value: combinedTotal ? (totalGrid / combinedTotal) * 100 : 0,
    },
    {
      name: "Solar",
      value: combinedTotal ? (totalSolar / combinedTotal) * 100 : 0,
    },
    {
      name: "Diesel",
      value: combinedTotal ? (totalDiesel / combinedTotal) * 100 : 0,
    },
  ];

  const operationHealth = [
    {
      label: "Solar Penetration",
      value: Number(kpiData?.solar_pct || 0),
      tone: "bg-[#10b981]",
    },
    {
      label: "Energy Savings Index",
      value: combinedTotal
        ? Number(((kpiData?.energy_saved || 0) / combinedTotal).toFixed(2)) * 10
        : 0,
      tone: "bg-[#2563eb]",
    },
    {
      label: "Cost Stability",
      value: combinedTotal
        ? Math.max(0, 100 - (totalDiesel / combinedTotal) * 100)
        : 0,
      tone: "bg-[#f59e0b]",
    },
  ];

  const insightCards = [
    {
      title: "Best Source Mix",
      text: `${(sourceMixData[1]?.value || 0).toFixed(1)}% from solar keeps operating costs stable.`,
      icon: ShieldCheck,
      accent: "text-[#0ea5a8]",
    },
    {
      title: "Cost Exposure",
      text: `Diesel share is ${(sourceMixData[2]?.value || 0).toFixed(1)}%. Lowering it improves margin resilience.`,
      icon: CircleDollarSign,
      accent: "text-[#2563eb]",
    },
  ];

  const smartInsights = Array.isArray(kpiData?.insights) ? kpiData.insights : [];
  const smartRecommendations = Array.isArray(kpiData?.recommendations)
    ? kpiData.recommendations
    : [];
  const insightsSource = kpiData?.insights_source || "fallback";

  return (
    <div className="space-y-8">
      {/* KPI Cards Grid */}
      <div>
        <h2 className="text-2xl font-bold section-title mb-4 flex items-center gap-2">
          <TrendingUp className="text-[var(--accent-500)]" size={28} />
          Key Performance Indicators
        </h2>
        {useSolarFallback && (
          <div className="mb-4 surface-card rounded-xl p-4 border border-[var(--accent-200)] bg-[var(--accent-50)]">
            <p className="text-sm text-[var(--text-primary)]">
              No solar records were found in the selected date range. Overview
              is using latest available solar data
              {activeSolarRange?.min_date && activeSolarRange?.max_date
                ? ` from ${activeSolarRange.min_date} to ${activeSolarRange.max_date}.`
                : "."}
            </p>
          </div>
        )}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
          <KPICard
            title="Total Energy"
            value={kpiData?.total_kwh || 0}
            unit="kWh"
            color="blue"
            icon={Zap}
          />
          <KPICard
            title="Solar Generated"
            value={totalSolar || kpiData?.solar_kwh || 0}
            unit="kWh"
            color="yellow"
            icon={Sun}
          />
          <KPICard
            title="Solar %"
            value={kpiData?.solar_pct || 0}
            unit="%"
            color="green"
          />
          <KPICard
            title="Total Cost"
            value={kpiData?.total_cost || 0}
            unit="INR"
            color="red"
            icon={DollarSign}
          />
          <KPICard
            title="Energy Saved"
            value={kpiData?.energy_saved || 0}
            unit="INR"
            color="green"
            icon={Leaf}
          />
          <KPICard
            title="Avg Temperature"
            value={kpiData?.avg_temp || 0}
            unit="°C"
            color="blue"
            icon={Thermometer}
          />
        </div>
      </div>

      {/* Charts */}
      <div>
        <h2 className="text-2xl font-bold section-title mb-4">Energy Trends</h2>
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          <StackedBarChart
            data={chartData}
            title="Daily Energy Mix"
            dataKeys={["Grid", "Solar", "Diesel"]}
            colors={["#2563eb", "#10b981", "#f59e0b"]}
          />
          <LineChartComponent
            data={chartData}
            title="Energy Distribution Trend"
            dataKeys={["Grid", "Solar", "Diesel"]}
            colors={["#2563eb", "#10b981", "#f59e0b"]}
          />
        </div>
      </div>

      {/* Added visual features */}
      <div className="grid grid-cols-1 xl:grid-cols-3 gap-6">
        <div className="xl:col-span-2">
          <DonutChart
            data={sourceMixData}
            title="Energy Source Contribution"
            colors={["#2563eb", "#10b981", "#f59e0b"]}
          />
        </div>
        <div className="surface-card rounded-2xl p-6">
          <h3 className="text-xl font-bold section-title mb-6">
            Operational Health
          </h3>
          <div className="space-y-5">
            {operationHealth.map((item) => (
              <div key={item.label}>
                <div className="flex items-center justify-between text-sm mb-2">
                  <span className="text-[var(--text-primary)] font-medium">
                    {item.label}
                  </span>
                  <span className="text-[var(--text-muted)]">
                    {Math.min(100, item.value).toFixed(1)}%
                  </span>
                </div>
                <div className="h-2.5 w-full bg-[var(--accent-100)] rounded-full overflow-hidden">
                  <div
                    className={`h-full ${item.tone}`}
                    style={{ width: `${Math.min(100, item.value)}%` }}
                  />
                </div>
              </div>
            ))}
          </div>
        </div>
      </div>

      {smartInsights.length > 0 || smartRecommendations.length > 0 ? (
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          <div className="surface-card rounded-2xl p-5">
            <div className="flex items-center justify-between mb-3">
              <h3 className="font-semibold text-[var(--text-primary)]">
                Insights
              </h3>
              <span className="text-xs px-2 py-1 rounded-full bg-[var(--accent-100)] text-[var(--text-muted)] uppercase tracking-wide">
                {insightsSource}
              </span>
            </div>
            <ul className="list-disc pl-5 space-y-2 text-sm text-[var(--text-muted)]">
              {smartInsights.map((item, idx) => (
                <li key={`insight-${idx}`}>{item}</li>
              ))}
            </ul>
          </div>

          <div className="surface-card rounded-2xl p-5">
            <h3 className="font-semibold text-[var(--text-primary)] mb-3">
              Recommendations
            </h3>
            <ul className="list-disc pl-5 space-y-2 text-sm text-[var(--text-muted)]">
              {smartRecommendations.map((item, idx) => (
                <li key={`recommendation-${idx}`}>{item}</li>
              ))}
            </ul>
          </div>
        </div>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          {insightCards.map((insight) => {
            const Icon = insight.icon;
            return (
              <div key={insight.title} className="surface-card rounded-2xl p-5">
                <div className="flex items-start gap-3">
                  <div className="h-10 w-10 rounded-xl bg-[var(--accent-100)] flex items-center justify-center">
                    <Icon className={insight.accent} size={20} />
                  </div>
                  <div>
                    <p className="font-semibold text-[var(--text-primary)]">
                      {insight.title}
                    </p>
                    <p className="text-sm text-[var(--text-muted)] mt-1">
                      {insight.text}
                    </p>
                  </div>
                </div>
              </div>
            );
          })}
        </div>
      )}

      {/* Data Table */}
      <div>
        <div className="flex justify-between items-center mb-4">
          <h2 className="text-2xl font-bold section-title">Detailed Data</h2>
          <ExportButton
            onClick={handleExport}
            isLoading={isExporting}
            label="Export Excel"
          />
        </div>
        <DataTable data={unifiedData?.data || []} hideColumns={[]} />
      </div>
    </div>
  );
};
