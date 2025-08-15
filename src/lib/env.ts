export const API_BASE_URL = (() => {
	const raw = import.meta.env.VITE_API_BASE_URL as string | undefined;
	if (!raw) throw new Error('[env] VITE_API_BASE_URL missing (e.g. https://ttprov5.onrender.com)');
	let b = raw.trim();
	if (b.startsWith('http://') && /onrender\.com/.test(b)) b = b.replace(/^http:\/\//, 'https://');
	return b.replace(/\/$/, '');
})(); 