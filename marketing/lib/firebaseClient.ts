import type { User } from 'firebase/auth';

const hasEnv = Boolean(
	process.env.NEXT_PUBLIC_FIREBASE_API_KEY &&
	process.env.NEXT_PUBLIC_FIREBASE_AUTH_DOMAIN &&
	process.env.NEXT_PUBLIC_FIREBASE_PROJECT_ID
);

let _inited = false;
let _warned = false;

function warnOnce(msg: string) {
	if (_warned) return;
	_warned = true;
	if (typeof console !== 'undefined') console.warn(msg);
}

// Safe stubs used when Firebase is not configured
export const auth: any = undefined;
export const googleProvider: any = undefined;

export async function signInWithGoogle(): Promise<User> {
	if (!hasEnv) {
		warnOnce('Firebase not configured on marketing app. Sign-in is disabled.');
		throw new Error('Firebase is not configured');
	}
	throw new Error('Firebase runtime not initialized');
}

export async function logout(): Promise<void> {
	if (!hasEnv) return;
}

export const signInAndVerify = async () => {
	warnOnce('Firebase not configured on marketing app. signInAndVerify is disabled.');
	throw new Error('Firebase is not configured');
};

export const debugFirebaseConfig = () => {
	return {
		configured: hasEnv,
		env: {
			NEXT_PUBLIC_FIREBASE_API_KEY: process.env.NEXT_PUBLIC_FIREBASE_API_KEY,
			NEXT_PUBLIC_FIREBASE_AUTH_DOMAIN: process.env.NEXT_PUBLIC_FIREBASE_AUTH_DOMAIN,
			NEXT_PUBLIC_FIREBASE_PROJECT_ID: process.env.NEXT_PUBLIC_FIREBASE_PROJECT_ID,
			NEXT_PUBLIC_API_BASE_URL: process.env.NEXT_PUBLIC_API_BASE_URL,
		},
	};
};

export const checkSession = async () => {
	const apiBaseUrl = process.env.NEXT_PUBLIC_API_BASE_URL;
	if (!apiBaseUrl) return null;
	try {
		const r = await fetch(`${apiBaseUrl}/api/auth/session`, { credentials: 'include' });
		if (!r.ok) return null;
		return r.json();
	} catch {
		return null;
	}
};

export const logoutSession = async () => {
	const apiBaseUrl = process.env.NEXT_PUBLIC_API_BASE_URL;
	if (!apiBaseUrl) return false;
	try {
		await fetch(`${apiBaseUrl}/api/auth/logout`, { method: 'POST', credentials: 'include' });
		return true;
	} catch {
		return false;
	}
};

if (typeof window !== 'undefined') {
	// expose debug helpers without crashing
	;(window as any).debugFirebaseConfig = debugFirebaseConfig;
	;(window as any).signInAndVerify = signInAndVerify;
	;(window as any).checkSession = checkSession;
	;(window as any).logoutSession = logoutSession;
}