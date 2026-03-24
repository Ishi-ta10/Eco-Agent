import { create } from "zustand";

export const useTabStore = create((set) => ({
  activeTab: "overview",

  setActiveTab: (tab) => set({ activeTab: tab }),
}));
