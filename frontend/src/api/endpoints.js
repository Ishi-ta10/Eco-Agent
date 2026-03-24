import apiClient from "./client";

// Data endpoints
export const dataAPI = {
  getUnified: (startDate, endDate) =>
    apiClient.get("/api/data/unified", {
      params: { start_date: startDate, end_date: endDate },
    }),
  getGrid: (startDate, endDate) =>
    apiClient.get("/api/data/grid", {
      params: { start_date: startDate, end_date: endDate },
    }),
  getSolar: (startDate, endDate) =>
    apiClient.get("/api/data/solar", {
      params: { start_date: startDate, end_date: endDate },
    }),
  getDiesel: (startDate, endDate) =>
    apiClient.get("/api/data/diesel", {
      params: { start_date: startDate, end_date: endDate },
    }),
  getDailySummary: (startDate, endDate) =>
    apiClient.get("/api/data/daily-summary", {
      params: { start_date: startDate, end_date: endDate },
    }),
};

// KPI endpoints
export const kpiAPI = {
  getOverview: (startDate, endDate) =>
    apiClient.get("/api/kpis/overview", {
      params: { start_date: startDate, end_date: endDate },
    }),
  getGrid: (startDate, endDate) =>
    apiClient.get("/api/kpis/grid", {
      params: { start_date: startDate, end_date: endDate },
    }),
  getSolar: (startDate, endDate) =>
    apiClient.get("/api/kpis/solar", {
      params: { start_date: startDate, end_date: endDate },
    }),
  getDiesel: (startDate, endDate) =>
    apiClient.get("/api/kpis/diesel", {
      params: { start_date: startDate, end_date: endDate },
    }),
};

// Export endpoints
export const exportAPI = {
  exportUnified: (startDate, endDate) =>
    apiClient.post(
      "/api/export/unified",
      {
        start_date: startDate,
        end_date: endDate,
      },
      { responseType: "blob" },
    ),
  exportGrid: (startDate, endDate) =>
    apiClient.post(
      "/api/export/grid",
      {
        start_date: startDate,
        end_date: endDate,
      },
      { responseType: "blob" },
    ),
  exportSolar: (startDate, endDate) =>
    apiClient.post(
      "/api/export/solar",
      {
        start_date: startDate,
        end_date: endDate,
      },
      { responseType: "blob" },
    ),
  exportDiesel: (startDate, endDate) =>
    apiClient.post(
      "/api/export/diesel",
      {
        start_date: startDate,
        end_date: endDate,
      },
      { responseType: "blob" },
    ),
  exportECS: () =>
    apiClient.post("/api/export/ecs", {}, { responseType: "blob" }),
};

// Scheduler endpoints
export const schedulerAPI = {
  getConfig: () => apiClient.get("/api/scheduler/config"),
  updateConfig: (config) => apiClient.put("/api/scheduler/config", config),
  getStatus: () => apiClient.get("/api/scheduler/status"),
  start: (sendTime) =>
    apiClient.post("/api/scheduler/start", { send_time: sendTime }),
  stop: () => apiClient.post("/api/scheduler/stop"),
  sendNow: () => apiClient.post("/api/scheduler/send-now"),
  getHistory: (limit = 10) =>
    apiClient.get("/api/scheduler/history", { params: { limit } }),
  uploadTemplate: (file) => {
    const formData = new FormData();
    formData.append("file", file);
    return apiClient.post("/api/scheduler/upload-template", formData, {
      headers: { "Content-Type": "multipart/form-data" },
    });
  },
};
