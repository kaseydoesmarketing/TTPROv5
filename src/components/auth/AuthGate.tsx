import React, { useEffect, useState } from "react";
import { useAuth0 } from "@auth0/auth0-react";
const API_BASE = import.meta.env.VITE_API_BASE_URL;

export const AuthGate: React.FC<{ children: React.ReactNode }> = ({ children }) => {
	const { isLoading, isAuthenticated, loginWithRedirect, getIdTokenClaims, error, logout } = useAuth0();
	const [handshaked, setHandshaked] = useState(false);
	const [handshakeError, setHandshakeError] = useState<string | null>(null);
	useEffect(() => {
		const doHandshake = async () => {
			const claims = await getIdTokenClaims();
			if (!claims) return;
			const idToken = (claims as any).__raw;
			const res = await fetch(`${API_BASE}/api/auth/login`, {
				method: "POST",
				headers: { Authorization: `Bearer ${idToken}` },
				credentials: "include",
			});
			if (!res.ok) throw new Error(await res.text());
			setHandshaked(true);
		};
		if (!isLoading && isAuthenticated && !handshaked) doHandshake().catch(e => setHandshakeError(e.message || "Handshake failed"));
	}, [isLoading, isAuthenticated, handshaked, getIdTokenClaims]);
	if (isLoading) return <div className="p-8">Loading…</div>;
	if (error) return <div className="p-8 text-red-600">Auth error: {error.message}</div>;
	if (isAuthenticated && handshakeError) {
		return <div className="p-8 text-red-600">Handshake error: {handshakeError}
			<button className="ml-4 underline" onClick={() => logout({ logoutParams: { returnTo: window.location.origin } })}>Log out</button>
		</div>;
	}
	if (!isAuthenticated) {
		return (
			<div className="min-h-screen flex items-center justify-center">
				<div className="max-w-md w-full bg-black text-white p-8 rounded-2xl shadow-xl">
					<h1 className="text-2xl font-bold mb-4">TitleTesterPro</h1>
					<p className="mb-6 opacity-80">Sign in to continue</p>
					<button onClick={() => loginWithRedirect()} className="w-full py-3 rounded-lg bg-white text-black font-semibold hover:opacity-90">Sign in</button>
				</div>
			</div>
		);
	}
	if (!handshaked) return <div className="p-8">Finalizing sign-in…</div>;
	return <>{children}</>;
}; 