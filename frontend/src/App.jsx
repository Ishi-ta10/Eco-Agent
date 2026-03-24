import React, { useEffect } from "react";
import { useTabStore } from "./store/tabStore";
import { useThemeStore } from "./store/themeStore";
import { DateRangeFilter } from "./components/common/DateRangeFilter";
import { OverviewTab } from "./components/tabs/OverviewTab";
import { GridTab } from "./components/tabs/GridTab";
import { SolarTab } from "./components/tabs/SolarTab";
import { DieselTab } from "./components/tabs/DieselTab";
import { SchedulerTab } from "./components/tabs/SchedulerTab";
import { Zap, Grid2X2, Sun, Fuel, Clock, Moon, SunMedium } from "lucide-react";

const TAB_ITEMS = [
  { id: "overview", label: "Overview", icon: Grid2X2 },
  { id: "grid", label: "Grid Supply", icon: Zap },
  { id: "solar", label: "Solar Panel", icon: Sun },
  { id: "diesel", label: "Diesel Generator", icon: Fuel },
  { id: "scheduler", label: "Scheduler", icon: Clock },
];

function App() {
  const { activeTab, setActiveTab } = useTabStore();
  const { theme, toggleTheme } = useThemeStore();

  useEffect(() => {
    document.documentElement.setAttribute("data-theme", theme);
  }, [theme]);

  return (
    <div className="app-shell min-h-screen">
      {/* Header */}
      <header className="app-header fixed inset-x-0 top-0 z-50">
        <div className="max-w-7xl mx-auto px-4 py-6 sm:px-6 lg:px-8">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-4">
              <div className="brand-chip p-3 rounded-xl">
                <Zap className="text-white" size={28} strokeWidth={2.5} />
              </div>
              <div>
                <h1 className="app-title text-3xl md:text-4xl font-bold">
                  Energy Dashboard
                </h1>
                <p className="app-subtitle text-sm mt-1">
                  Real-time Energy Monitoring and Analytics
                </p>
              </div>
            </div>
            <button
              onClick={toggleTheme}
              className="theme-toggle-btn"
              aria-label="Toggle theme"
              title={`Switch to ${theme === "light" ? "dark" : "light"} mode`}
            >
              {theme === "light" ? <Moon size={16} /> : <SunMedium size={16} />}
              {theme === "light" ? "Dark" : "Light"}
            </button>
          </div>
        </div>
      </header>

      {/* Main Content */}
      <main className="max-w-7xl mx-auto px-4 pt-40 pb-8 sm:px-6 lg:px-8">
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-8 fade-in-up">
          <div className="surface-card rounded-2xl p-4">
            <p className="text-xs uppercase tracking-wide text-[var(--text-muted)]">
              Data Confidence
            </p>
            <p className="text-2xl font-bold text-[var(--text-primary)] mt-1">
              99.2%
            </p>
          </div>
          <div className="surface-card rounded-2xl p-4">
            <p className="text-xs uppercase tracking-wide text-[var(--text-muted)]">
              Response Latency
            </p>
            <p className="text-2xl font-bold text-[var(--text-primary)] mt-1">
              1.4s
            </p>
          </div>
          <div className="surface-card rounded-2xl p-4">
            <p className="text-xs uppercase tracking-wide text-[var(--text-muted)]">
              Last Refresh
            </p>
            <p className="text-2xl font-bold text-[var(--text-primary)] mt-1">
              Just now
            </p>
          </div>
        </div>

        {/* Date Range Filter */}
        <div className="mb-8">
          <div className="surface-card rounded-2xl p-6 fade-in-up">
            <h2 className="section-title font-semibold mb-4 flex items-center gap-2">
              <span className="w-1 h-6 bg-[var(--accent-500)] rounded"></span>
              Filter by Date Range
            </h2>
            <DateRangeFilter />
          </div>
        </div>

        {/* Tab Navigation */}
        <div className="mb-8">
          <div className="nav-shell flex gap-2 rounded-2xl p-2 overflow-x-auto fade-in-up">
            {TAB_ITEMS.map((tab) => {
              const IconComponent = tab.icon;
              const isActive = activeTab === tab.id;
              return (
                <button
                  key={tab.id}
                  onClick={() => setActiveTab(tab.id)}
                  className={`nav-btn ${isActive ? "nav-btn-active" : ""}`}
                >
                  <IconComponent size={18} />
                  {tab.label}
                </button>
              );
            })}
          </div>
        </div>

        {/* Tab Content */}
        <div className="surface-card rounded-2xl overflow-hidden fade-in-up">
          <div className="p-6 md:p-8">
            {activeTab === "overview" && <OverviewTab />}
            {activeTab === "grid" && <GridTab />}
            {activeTab === "solar" && <SolarTab />}
            {activeTab === "diesel" && <DieselTab />}
            {activeTab === "scheduler" && <SchedulerTab />}
          </div>
        </div>
      </main>

      {/* Footer */}
      <footer className="footer-shell mt-12">
        <div className="max-w-7xl mx-auto px-4 py-8 sm:px-6 lg:px-8">
          <div className="grid grid-cols-1 md:grid-cols-3 gap-8 mb-8">
            <div>
              <h3 className="section-title font-semibold mb-2">
                Energy Dashboard
              </h3>
              <p className="text-sm text-[var(--text-muted)]">
                Real-time monitoring and analytics for energy consumption
              </p>
            </div>
            <div>
              <h3 className="section-title font-semibold mb-2">Features</h3>
              <ul className="text-sm text-[var(--text-muted)] space-y-1">
                <li>• Live Energy Tracking</li>
                <li>• Performance Analytics</li>
                <li>• Automated Exports</li>
              </ul>
            </div>
            <div>
              <h3 className="section-title font-semibold mb-2">Status</h3>
              <p className="text-sm text-[var(--success-600)]">
                ✓ All Systems Operational
              </p>
            </div>
          </div>
          <div className="border-t border-[var(--surface-border)] pt-6 text-center text-sm text-[var(--text-muted)]">
            <p>&copy; 2026 Energy Dashboard. Powered by React + FastAPI</p>
          </div>
        </div>
      </footer>
    </div>
  );
}

export default App;
