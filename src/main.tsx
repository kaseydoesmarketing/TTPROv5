import { StrictMode } from 'react'
import { createRoot } from 'react-dom/client'
import { Auth0Provider } from '@auth0/auth0-react'
import './index.css'
import App from './App.tsx'

const root = document.getElementById('root')!

const domain = import.meta.env.VITE_AUTH0_DOMAIN
const clientId = import.meta.env.VITE_AUTH0_CLIENT_ID
const apiBase = import.meta.env.VITE_API_BASE_URL

if (!domain || !clientId || !apiBase) {
	const missing = [
		!domain ? 'VITE_AUTH0_DOMAIN' : null,
		!clientId ? 'VITE_AUTH0_CLIENT_ID' : null,
		!apiBase ? 'VITE_API_BASE_URL' : null,
	].filter(Boolean).join(', ')
	root.innerHTML = `
		<div style="min-height:100vh;display:flex;align-items:center;justify-content:center;background:#0b0b0b;color:#fff;font-family:system-ui,sans-serif;">
			<div style="max-width:720px;padding:24px;border-radius:12px;background:#111;border:1px solid #333;">
				<h1 style="margin:0 0 12px;font-size:20px;">Configuration error</h1>
				<p style="margin:0 0 8px;opacity:.9;">Missing required environment variables:</p>
				<pre style="white-space:pre-wrap;background:#0b0b0b;padding:12px;border-radius:8px;border:1px solid #333;">${missing}</pre>
				<p style="margin:12px 0 0;opacity:.8;">Set these in your build environment and redeploy. Example:</p>
				<pre style="white-space:pre-wrap;background:#0b0b0b;padding:12px;border-radius:8px;border:1px solid #333;">VITE_API_BASE_URL=https://ttprov5.onrender.com</pre>
			</div>
		</div>
	`
} else {
	const onRedirectCallback = (appState?: any) => {
		const target = appState?.returnTo || '/app'
		if (window.location.pathname !== target) {
			window.history.replaceState({}, document.title, target)
		}
	}

	createRoot(root).render(
		<StrictMode>
			<Auth0Provider
				domain={domain}
				clientId={clientId}
				authorizationParams={{ redirect_uri: `${window.location.origin}/auth/callback` }}
				onRedirectCallback={onRedirectCallback}
			>
				<App />
			</Auth0Provider>
		</StrictMode>,
	)
}
