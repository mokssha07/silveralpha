const BASE_URL = process.env.NEXT_PUBLIC_API_BASE;

async function apiFetch(path) {
  const res = await fetch(`${BASE_URL}${path}`);
  if (!res.ok) {
    throw new Error(`API error: ${res.status}`);
  }
  return res.json();
}

// API endpoints
export const getStatus = () => apiFetch("/status/");
export const getGlobeNodes = () => apiFetch("/globe/nodes/");
export const getNodeDetail = (id) => apiFetch(`/node/${id}/`);
export const getDashboardSummary = () => apiFetch("/dashboard/summary/");
export const getChartData = () => apiFetch("/dashboard/chart/");
