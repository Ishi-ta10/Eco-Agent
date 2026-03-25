import axios from "axios";

const configuredApiUrl = import.meta.env.VITE_API_URL?.trim();

const API_BASE_URLS = [
  configuredApiUrl,
  "http://localhost:8000",
  "http://127.0.0.1:8000",
  "http://localhost:8890",
  "http://127.0.0.1:8890",
].filter((url, index, list) => url && list.indexOf(url) === index);

let activeApiBaseUrl = API_BASE_URLS[0] || "http://localhost:8000";

const apiClient = axios.create({
  baseURL: activeApiBaseUrl,
  headers: {
    "Content-Type": "application/json",
  },
});

// Add request interceptor for loading states if needed
apiClient.interceptors.request.use(
  (config) => {
    return config;
  },
  (error) => {
    return Promise.reject(error);
  },
);

// Add response interceptor for error handling
apiClient.interceptors.response.use(
  (response) => response,
  (error) => {
    const originalRequest = error.config;

    if (error?.code === "ERR_NETWORK" && originalRequest) {
      const attemptedUrls = originalRequest.__attemptedBaseUrls || [
        originalRequest.baseURL || activeApiBaseUrl,
      ];

      const nextBaseUrl = API_BASE_URLS.find(
        (url) => !attemptedUrls.includes(url),
      );

      if (nextBaseUrl) {
        originalRequest.__attemptedBaseUrls = [...attemptedUrls, nextBaseUrl];
        originalRequest.baseURL = nextBaseUrl;
        activeApiBaseUrl = nextBaseUrl;
        apiClient.defaults.baseURL = nextBaseUrl;
        console.warn(`Retrying API request with fallback URL: ${nextBaseUrl}`);
        return apiClient.request(originalRequest);
      }
    }

    console.error("API Error:", error);
    return Promise.reject(error);
  },
);

export default apiClient;
