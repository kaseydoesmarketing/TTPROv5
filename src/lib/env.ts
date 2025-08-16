export const API_BASE_URL = (() => {
	const raw = import.meta.env.VITE_API_BASE_URL as string | undefined;
	if (!raw) throw new Error('[env] VITE_API_BASE_URL missing (e.g. https://ttprov5.onrender.com or /api)');
	let b = raw.trim();
	// Prefer same-origin on production to avoid third‑party cookies; API paths already start with /api
	if (typeof window !== 'undefined') {
		const h = window.location.hostname;
		if (/titletesterpro\.com$/.test(h) && /onrender\.com/.test(b)) {
			return '';
		}
	}
	if (b.startsWith('/')) {
		return b.replace(/\/$/, '');
	}
	if (b.startsWith('http://') && /onrender\.com/.test(b)) b = b.replace(/^http:\/\//, 'https://');
	return b.replace(/\/$/, '');
})(); 