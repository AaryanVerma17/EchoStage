const BASE = import.meta.env.VITE_API_BASE_URL || 'http://127.0.0.1:8000';
async function request(path, options = {}) {
  const res = await fetch(`${BASE}${path}`, { headers: {'Content-Type':'application/json', ...(options.headers || {})}, ...options });
  const data = await res.json().catch(() => ({}));
  if (!res.ok) throw new Error(data.detail || `Request failed (${res.status})`);
  return data;
}
export const api = {
  health: () => request('/health'),
  decide: state => request('/api/decide', {method:'POST', body:JSON.stringify({state})}),
  brief: (theme, style) => request('/api/scene-brief', {method:'POST', body:JSON.stringify({theme,style})}),
  events: () => request('/api/events?limit=30'),
  reset: () => request('/api/reset', {method:'POST'})
};
