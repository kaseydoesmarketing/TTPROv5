export const API_BASE_URL = (() => {
	const raw = import.meta.env.VITE_API_BASE_URL as string | undefined;
	if (!raw) throw new Error('[env] VITE_API_BASE_URL missing (e.g. https://ttprov5.onrender.com or /api)');
	let b = raw.trim();
	// Support relative base for same-origin proxying (e.g. '/api')
	if (b.startsWith('/')) {
		// normalize to no trailing slash
		return b.replace(/\/$/, '');
	}
	// Absolute URL path: enforce HTTPS for Render and strip trailing slash
	if (b.startsWith('http://') && /onrender\.com/.test(b)) b = b.replace(/^http:\/\//, 'https://');
	return b.replace(/\/$/, '');
})(); 