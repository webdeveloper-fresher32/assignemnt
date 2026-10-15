import axios from 'axios';

const API_BASE = import.meta.env.VITE_API_URL || '/api/v1';

const apiClient = axios.create({
  baseURL: API_BASE,
  timeout: 30000,
  headers: {
    'Content-Type': 'application/json',
  },
});

export const fetchHazardAnalysis = async (params) => {
  const response = await apiClient.post('/hazards/analyze', params);
  return response.data;
};

export const searchLocations = async (query) => {
  if (!query || query.trim().length < 2) return [];
  const response = await apiClient.get('/geocoding/search', {
    params: { q: query.trim() },
  });
  return response.data;
};

export const checkHealth = async () => {
  const response = await apiClient.get('/health');
  return response.data;
};

export const downloadCsv = async (params) => {
  const response = await apiClient.post('/hazards/export/csv', params, {
    responseType: 'blob',
  });
  const url = window.URL.createObjectURL(new Blob([response.data]));
  const link = document.createElement('a');
  link.href = url;
  const filename = `climate_hazard_${(params.region_name || 'analysis').replace(/\s+/g, '_').toLowerCase()}_${params.start_year}_${params.end_year}.csv`;
  link.setAttribute('download', filename);
  document.body.appendChild(link);
  link.click();
  link.remove();
  window.URL.revokeObjectURL(url);
};

export const downloadPdf = async (params) => {
  const response = await apiClient.post('/hazards/export/pdf', params, {
    responseType: 'blob',
  });
  const url = window.URL.createObjectURL(new Blob([response.data], { type: 'application/pdf' }));
  const link = document.createElement('a');
  link.href = url;
  const filename = `climate_hazard_report_${(params.region_name || 'analysis').replace(/\s+/g, '_').toLowerCase()}.pdf`;
  link.setAttribute('download', filename);
  document.body.appendChild(link);
  link.click();
  link.remove();
  window.URL.revokeObjectURL(url);
};
