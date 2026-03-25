import React, { useEffect, useMemo, useState } from "react";
import { useQueryClient } from "@tanstack/react-query";
import { useTabStore } from "./store/tabStore";
import { useThemeStore } from "./store/themeStore";
import { OverviewTab } from "./components/tabs/OverviewTab";
import { GridTab } from "./components/tabs/GridTab";
import { SolarTab } from "./components/tabs/SolarTab";
import { DieselTab } from "./components/tabs/DieselTab";
import { SchedulerTab } from "./components/tabs/SchedulerTab";
import { FiltersTab } from "./components/tabs/FiltersTab";
import {
  BellRing,
  Clock3,
  Fuel,
  Grid2X2,
  Moon,
  PanelLeftClose,
  PanelLeftOpen,
  RefreshCw,
  SlidersHorizontal,
  Sun,
  SunMedium,
  Zap,
} from "lucide-react";

const TAB_ITEMS = [
  {
    id: "overview",
    label: "Overview",
    icon: Grid2X2,
    description: "Executive operations board",
  },
  {
    id: "grid",
    label: "Grid Supply",
    icon: Zap,
    description: "Supply and tariff intelligence",
  },
  {
    id: "solar",
    label: "Solar Panel",
    icon: Sun,
    description: "Generation and inverter health",
  },
  {
    id: "diesel",
    label: "Diesel Generator",
    icon: Fuel,
    description: "Fuel and runtime performance",
  },
  {
    id: "scheduler",
    label: "Scheduler",
    icon: Clock3,
    description: "Mail automation operations",
  },
  {
    id: "filters",
    label: "Filters",
    icon: SlidersHorizontal,
    description: "Date and reporting controls",
  },
];

function App() {
  const queryClient = useQueryClient();
  const { activeTab, setActiveTab } = useTabStore();
  const { theme, toggleTheme } = useThemeStore();
  const [lastRefresh, setLastRefresh] = useState(new Date());
  const [isSidebarCollapsed, setIsSidebarCollapsed] = useState(false);

  useEffect(() => {
    document.documentElement.setAttribute("data-theme", theme);
  }, [theme]);

  const activeTabItem = useMemo(
    () => TAB_ITEMS.find((item) => item.id === activeTab) || TAB_ITEMS[0],
    [activeTab],
  );

  const handleManualRefresh = async () => {
    await queryClient.invalidateQueries();
    setLastRefresh(new Date());
  };

  const renderTabContent = () => {
    if (activeTab === "overview") return <OverviewTab />;
    if (activeTab === "grid") return <GridTab />;
    if (activeTab === "solar") return <SolarTab />;
    if (activeTab === "diesel") return <DieselTab />;
    if (activeTab === "scheduler") return <SchedulerTab />;
    if (activeTab === "filters") return <FiltersTab />;
    return <OverviewTab />;
  };

  return (
    <div className="enterprise-shell">
      <aside
        className={`enterprise-sidebar ${isSidebarCollapsed ? "collapsed" : ""}`}
      >
        <div className="sidebar-top">
          <div className="brand-lockup">
            <div className="brand-mark">
              <Zap className="text-white" size={22} strokeWidth={2.6} />
            </div>
            <div>
              <h1 className="text-lg font-semibold app-title">
                Energy Command
              </h1>
              <p className="text-xs app-subtitle">
                Enterprise Operations Center
              </p>
            </div>
          </div>
          <button
            type="button"
            className="theme-toggle-btn hidden lg:inline-flex"
            onClick={() => setIsSidebarCollapsed((state) => !state)}
            title={isSidebarCollapsed ? "Expand sidebar" : "Collapse sidebar"}
            aria-label={
              isSidebarCollapsed ? "Expand sidebar" : "Collapse sidebar"
            }
          >
            {isSidebarCollapsed ? (
              <PanelLeftOpen size={16} />
            ) : (
              <PanelLeftClose size={16} />
            )}
          </button>
        </div>

        <nav className="nav-rail">
          {TAB_ITEMS.map((tab) => {
            const IconComponent = tab.icon;
            const isActive = activeTab === tab.id;

            return (
              <button
                type="button"
                key={tab.id}
                onClick={() => {
                  setActiveTab(tab.id);
                }}
                className={`nav-rail-btn ${isActive ? "nav-rail-btn-active" : ""}`}
              >
                <IconComponent size={18} />
                <span>{tab.label}</span>
                {!isSidebarCollapsed && (
                  <small className="nav-rail-meta">{tab.description}</small>
                )}
              </button>
            );
          })}
        </nav>
      </aside>

      <div className="workspace">
        <header className="workspace-header">
          <div className="workspace-header-left">
            <div>
              <h2 className="text-2xl md:text-3xl font-bold app-title">
                {activeTabItem.label}
              </h2>
              <p className="app-subtitle">{activeTabItem.description}</p>
            </div>
          </div>
        </header>

        <main className="workspace-main">
          <section className="surface-card rounded-2xl px-5 py-4 md:px-6 md:py-5 fade-in-up">
            <div className="grid grid-cols-1 gap-3">
              <div>
                <p className="text-xs uppercase tracking-wide text-[var(--text-muted)]">
                  Last Refresh
                </p>
                <p className="text-sm md:text-base font-semibold text-[var(--text-primary)] mt-1">
                  {lastRefresh.toLocaleString("en-IN")}
                </p>
              </div>
            </div>
          </section>

          <section className="dashboard-panel surface-card rounded-3xl p-5 md:p-8 fade-in-up">
            {renderTabContent()}
          </section>
        </main>

        <footer className="footer-shell px-5 py-4 md:px-8">
          <p className="text-sm text-[var(--text-muted)]">
            Energy Command Dashboard | Enterprise Edition | React + FastAPI
          </p>
        </footer>
      </div>
    </div>
  );
}

export default App;
