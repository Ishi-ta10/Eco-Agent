import { create } from "zustand";

const THEME_STORAGE_KEY = "energy-dashboard-theme";

const getInitialTheme = () => {
  const stored = localStorage.getItem(THEME_STORAGE_KEY);
  if (stored === "light" || stored === "dark") {
    return stored;
  }
  return "light";
};

export const useThemeStore = create((set) => ({
  theme: getInitialTheme(),
  setTheme: (theme) => {
    if (theme !== "light" && theme !== "dark") return;
    localStorage.setItem(THEME_STORAGE_KEY, theme);
    set({ theme });
  },
  toggleTheme: () =>
    set((state) => {
      const nextTheme = state.theme === "light" ? "dark" : "light";
      localStorage.setItem(THEME_STORAGE_KEY, nextTheme);
      return { theme: nextTheme };
    }),
}));
