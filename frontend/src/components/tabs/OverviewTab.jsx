import React, { useState } from "react";
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
  asNumber,
  EFFECTIVE_TODAY,
  EFFECTIVE_TODAY_DISPLAY,
  getLatestRow,
  getRecentDateRange,
  getRecentRows,
  getRowsForDate,
} from "../../utils/recentData";
import {
  Zap,
  Sun,
  DollarSign,
  Leaf,
  TrendingUp,
  ShieldCheck,
  CircleDollarSign,
} from "lucide-react";

const buildOverviewChartData = (rows = []) => {
  const groupedByDate = rows.reduce((acc, row) => {
    const date = row?.Date || "Unknown";
    if (!acc[date]) {
      acc[date] = {
        Date: date,
        "Grid Energy Consumed (kWh)": 0,
        "Solar Energy Generated (kWh)": 0,
        "Diesel Generator Energy Consumed (kWh)": 0,
      };
    }

    acc[date]["Grid Energy Consumed (kWh)"] += asNumber(row, [
      "Grid KWh",
      "Grid Units Consumed (KWh)",
    ]);
    acc[date]["Solar Energy Generated (kWh)"] += asNumber(row, [
      "Solar KWh",
      "Solar Units Generated (KWh)",
    ]);
    acc[date]["Diesel Generator Energy Consumed (kWh)"] += asNumber(row, [
      "Diesel KWh",
      "DG Units Consumed (KWh)",
    ]);
    return acc;
  }, {});

  return Object.values(groupedByDate).sort((a, b) =>
    String(a.Date).localeCompare(String(b.Date)),
  );
};

const applyMixedDateWording = (items = [], displayDate) => {
  const styles = ["prefixToday", "prefixDate", "suffixToday"];

  const capitalizeStart = (text = "") =>
    text.replace(
      /^(\s*)([a-z])/,
      (match, leading, chr) => `${leading}${chr.toUpperCase()}`,
    );

  return items.map((item, idx) => {
    const style = styles[idx % styles.length];
    const raw = String(item || "")
      .replace(/\{current_date\}/gi, displayDate)
      .trim();

    const withoutLeadingDate = raw.replace(
      /^as of\s+(today|\d{2}-\d{2}-\d{4}|\d{4}-\d{2}-\d{2})\s*,?\s*/i,
      "",
    );
    const withoutTrailingDate = withoutLeadingDate.replace(
      /\s*,?\s*as of\s+(today|\d{2}-\d{2}-\d{4}|\d{4}-\d{2}-\d{2})\.?\s*$/i,
      "",
    );
    const core = capitalizeStart(withoutTrailingDate.trim());

    if (!core) return raw;

    const sentence = /[.!?]$/.test(core) ? core : `${core}.`;

    if (style === "prefixToday") {
      return `As of today, ${sentence}`;
    }

    if (style === "prefixDate") {
      return `As of ${displayDate}, ${sentence}`;
    }

    return `${sentence.replace(/[.!?]+$/, "")} as of today.`;
  });
};

export const OverviewTab = () => {
  const [isExporting, setIsExporting] = useState(false);
  const { startDate, endDate } = getRecentDateRange(7);

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

  if (dataError || solarError || fallbackSolarError) {
    return (
      <div className="text-center py-12">
        <p className="text-[var(--danger-600)] text-lg">
          Error loading data. Please check backend connection.
        </p>
        <p className="text-[var(--text-muted)] mt-2">
          {dataError?.message || solarError?.message}
        </p>
      </div>
    );
  }

  const recentUnifiedRows = getRecentRows(unifiedData?.data || [], 7);
  const todayUnifiedRows = getRowsForDate(recentUnifiedRows, EFFECTIVE_TODAY);
  const latestUnifiedRow = getLatestRow(todayUnifiedRows);

  const selectedSolarRows = solarData?.data || [];
  const fallbackSolarRows = fallbackSolarData?.data || [];
  const useSolarFallback =
    selectedSolarRows.length === 0 && fallbackSolarRows.length > 0;
  const activeSolarRows = getRecentRows(
    useSolarFallback ? fallbackSolarRows : selectedSolarRows,
    7,
  );
  const todaySolarRows = getRowsForDate(activeSolarRows, EFFECTIVE_TODAY);
  const latestSolarRow = getLatestRow(todaySolarRows);

  const chartData = buildOverviewChartData(recentUnifiedRows);

  const latestTotalEnergyConsumed = asNumber(latestUnifiedRow, [
    "Total Units Consumed (KWh)",
    "Total KWh",
    "Total Energy",
  ]);
  const latestSolarEnergyGenerated =
    asNumber(latestUnifiedRow, ["Solar Units Generated (KWh)", "Solar KWh"]) ||
    asNumber(latestSolarRow, ["Solar Units Generated (KWh)", "Solar KWh"]);
  const latestTotalEnergyCost = asNumber(latestUnifiedRow, [
    "Total Cost (INR)",
    "Total Cost",
    "Cost",
  ]);
  const latestEstimatedSavings = asNumber(latestUnifiedRow, [
    "Energy Saving (INR)",
    "Energy Saved (INR)",
    "Energy Saved",
    "Savings",
  ]);
  const latestSolarContribution = latestTotalEnergyConsumed
    ? (latestSolarEnergyGenerated / latestTotalEnergyConsumed) * 100
    : 0;

  const activeSolarRange = useSolarFallback
    ? fallbackSolarData?.date_range
    : solarData?.date_range;

  const totalGrid = chartData.reduce(
    (sum, row) => sum + row["Grid Energy Consumed (kWh)"],
    0,
  );
  const totalSolar = chartData.reduce(
    (sum, row) => sum + row["Solar Energy Generated (kWh)"],
    0,
  );
  const totalDiesel = chartData.reduce(
    (sum, row) => sum + row["Diesel Generator Energy Consumed (kWh)"],
    0,
  );
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

  const insightCards = [
    {
      title: "Best Source Mix",
      text: `${(sourceMixData[1]?.value || 0).toFixed(1)}% from solar keeps operating costs stable.`,
      icon: ShieldCheck,
      accent: "text-[#4f8d7d]",
    },
    {
      title: "Cost Exposure",
      text: `Diesel share is ${(sourceMixData[2]?.value || 0).toFixed(1)}%. Lowering it improves margin resilience.`,
      icon: CircleDollarSign,
      accent: "text-[#3f6894]",
    },
  ];

  const smartInsights = Array.isArray(kpiData?.insights)
    ? applyMixedDateWording(kpiData.insights, EFFECTIVE_TODAY_DISPLAY)
    : [];
  const smartRecommendations = Array.isArray(kpiData?.recommendations)
    ? applyMixedDateWording(kpiData.recommendations, EFFECTIVE_TODAY_DISPLAY)
    : [];
  const insightsSource = kpiError
    ? "fallback"
    : kpiData?.insights_source || "fallback";

  return (
    <div className="space-y-8">
      {/* KPI Cards Grid */}
      <div>
        <h2 className="text-2xl font-bold section-title mb-4 flex items-center gap-2">
          <TrendingUp className="text-[var(--accent-500)]" size={28} />
          Key Metrics of Today
        </h2>
        <p className="text-sm text-[var(--text-muted)] mb-4">
          Date: {EFFECTIVE_TODAY_DISPLAY}
        </p>
        {useSolarFallback && (
          <div className="mb-4 surface-card rounded-xl p-4 border border-[var(--accent-200)] bg-[var(--accent-50)]">
            <p className="text-sm text-[var(--text-primary)]">
              No solar records were found in the selected date range. Overview
              is using the latest available solar day
              {activeSolarRange?.min_date && activeSolarRange?.max_date
                ? ` from ${activeSolarRange.min_date} to ${activeSolarRange.max_date}.`
                : "."}
            </p>
          </div>
        )}
        <div className="grid grid-cols-3 gap-4">
          <KPICard
            title="Total Energy Consumed"
            value={latestTotalEnergyConsumed}
            unit="kWh"
            color="blue"
            icon={Zap}
          />
          <KPICard
            title="Solar Energy Generated"
            value={latestSolarEnergyGenerated}
            unit="kWh"
            color="yellow"
            icon={Sun}
          />
          <KPICard
            title="Solar Contribution To Consumption"
            value={latestSolarContribution}
            unit="%"
            color="green"
          />
          <KPICard
            title="Total Energy Cost"
            value={latestTotalEnergyCost}
            unit="INR"
            color="red"
            icon={DollarSign}
          />
          <KPICard
            title="Estimated Energy Cost Savings"
            value={latestEstimatedSavings}
            unit="INR"
            color="green"
            icon={Leaf}
          />
        </div>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        <div className="surface-card rounded-2xl p-5">
          <div className="flex items-center justify-between mb-3">
            <h3 className="font-semibold text-[var(--text-primary)]">
              Smart Insights
            </h3>
            <span className="text-xs px-2 py-1 rounded-full bg-[var(--accent-100)] text-[var(--text-muted)] uppercase tracking-wide">
              {insightsSource}
            </span>
          </div>
          {smartInsights.length > 0 ? (
            <ul className="list-disc pl-5 space-y-2 text-sm text-[var(--text-muted)]">
              {smartInsights.map((item, idx) => (
                <li key={`insight-${idx}`}>{item}</li>
              ))}
            </ul>
          ) : (
            <ul className="list-disc pl-5 space-y-2 text-sm text-[var(--text-muted)]">
              {insightCards.map((item, idx) => (
                <li key={`fallback-insight-${idx}`}>{item.text}</li>
              ))}
            </ul>
          )}
        </div>

        <div className="surface-card rounded-2xl p-5">
          <h3 className="font-semibold text-[var(--text-primary)] mb-3">
            Smart Recommendations
          </h3>
          {smartRecommendations.length > 0 ? (
            <ul className="list-disc pl-5 space-y-2 text-sm text-[var(--text-muted)]">
              {smartRecommendations.map((item, idx) => (
                <li key={`recommendation-${idx}`}>{item}</li>
              ))}
            </ul>
          ) : (
            <p className="text-sm text-[var(--text-muted)]">
              Recommendations are generated when enough context is available in
              the selected 7-day window ending on 2026-03-22.
            </p>
          )}
        </div>
      </div>

      {/* Charts */}
      <div>
        <h2 className="text-2xl font-bold section-title mb-4">
          Energy Trends (Last 7 Days)
        </h2>
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          <StackedBarChart
            data={chartData}
            title="Daily Energy Mix (Last 7 Days)"
            dataKeys={[
              "Grid Energy Consumed (kWh)",
              "Solar Energy Generated (kWh)",
              "Diesel Generator Energy Consumed (kWh)",
            ]}
            colors={["#3f6894", "#4f8d7d", "#b68656"]}
          />
          <LineChartComponent
            data={chartData}
            title="Energy Distribution Trend (Last 7 Days)"
            dataKeys={[
              "Grid Energy Consumed (kWh)",
              "Solar Energy Generated (kWh)",
              "Diesel Generator Energy Consumed (kWh)",
            ]}
            colors={["#3f6894", "#4f8d7d", "#b68656"]}
          />
        </div>
      </div>

      {/* Added visual features */}
      <DonutChart
        data={sourceMixData}
        title="Energy Source Contribution"
        colors={["#3f6894", "#4f8d7d", "#b68656"]}
      />

      {/* Data Table */}
      <div>
        <div className="flex justify-between items-center mb-4">
          <h2 className="text-2xl font-bold section-title">
            Detailed Data (Last 7 Days)
          </h2>
          <ExportButton
            onClick={handleExport}
            isLoading={isExporting}
            label="Export Excel"
          />
        </div>
        <DataTable
          data={recentUnifiedRows}
          hideColumns={["DG ID", "DG Id", "DGID"]}
        />
      </div>
    </div>
  );
};
