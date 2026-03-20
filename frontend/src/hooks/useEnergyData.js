import { useQuery } from '@tanstack/react-query';
import { dataAPI, kpiAPI } from '../api/endpoints';

// Data fetching hooks using TanStack Query

export const useUnifiedData = (startDate, endDate) => {
  return useQuery({
    queryKey: ['unified-data', startDate, endDate],
    queryFn: () => dataAPI.getUnified(startDate, endDate).then((res) => res.data),
    staleTime: 5 * 60 * 1000, // 5 minutes
    gcTime: 10 * 60 * 1000, // 10 minutes (formerly cacheTime)
  });
};

export const useGridData = (startDate, endDate) => {
  return useQuery({
    queryKey: ['grid-data', startDate, endDate],
    queryFn: () => dataAPI.getGrid(startDate, endDate).then((res) => res.data),
    staleTime: 5 * 60 * 1000,
    gcTime: 10 * 60 * 1000,
  });
};

export const useSolarData = (startDate, endDate) => {
  return useQuery({
    queryKey: ['solar-data', startDate, endDate],
    queryFn: () => dataAPI.getSolar(startDate, endDate).then((res) => res.data),
    staleTime: 5 * 60 * 1000,
    gcTime: 10 * 60 * 1000,
  });
};

export const useDieselData = (startDate, endDate) => {
  return useQuery({
    queryKey: ['diesel-data', startDate, endDate],
    queryFn: () => dataAPI.getDiesel(startDate, endDate).then((res) => res.data),
    staleTime: 5 * 60 * 1000,
    gcTime: 10 * 60 * 1000,
  });
};

export const useDailySummary = (startDate, endDate) => {
  return useQuery({
    queryKey: ['daily-summary', startDate, endDate],
    queryFn: () => dataAPI.getDailySummary(startDate, endDate).then((res) => res.data),
    staleTime: 5 * 60 * 1000,
    gcTime: 10 * 60 * 1000,
  });
};

// KPI hooks
export const useOverviewKPIs = (startDate, endDate) => {
  return useQuery({
    queryKey: ['overview-kpis', startDate, endDate],
    queryFn: () => kpiAPI.getOverview(startDate, endDate).then((res) => res.data),
    staleTime: 5 * 60 * 1000,
    gcTime: 10 * 60 * 1000,
  });
};

export const useGridKPIs = (startDate, endDate) => {
  return useQuery({
    queryKey: ['grid-kpis', startDate, endDate],
    queryFn: () => kpiAPI.getGrid(startDate, endDate).then((res) => res.data),
    staleTime: 5 * 60 * 1000,
    gcTime: 10 * 60 * 1000,
  });
};

export const useSolarKPIs = (startDate, endDate) => {
  return useQuery({
    queryKey: ['solar-kpis', startDate, endDate],
    queryFn: () => kpiAPI.getSolar(startDate, endDate).then((res) => res.data),
    staleTime: 5 * 60 * 1000,
    gcTime: 10 * 60 * 1000,
  });
};

export const useDieselKPIs = (startDate, endDate) => {
  return useQuery({
    queryKey: ['diesel-kpis', startDate, endDate],
    queryFn: () => kpiAPI.getDiesel(startDate, endDate).then((res) => res.data),
    staleTime: 5 * 60 * 1000,
    gcTime: 10 * 60 * 1000,
  });
};
