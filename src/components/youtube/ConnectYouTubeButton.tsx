import React from 'react';
import { useAuth0 } from '@auth0/auth0-react';

export function ConnectYouTubeButton() {
	const { loginWithRedirect, user } = useAuth0();

	const connect = async () => {
		const disableScopes = import.meta.env.VITE_DISABLE_YOUTUBE_SCOPE === '1';
		await loginWithRedirect({
			authorizationParams: {
				connection: 'google-oauth2',
				prompt: 'consent',
				access_type: 'offline',
				scope: 'openid profile email offline_access',
				// request IdP-level scopes for Google (optional via flag)
				...(disableScopes ? {} : { connection_scope: 'https://www.googleapis.com/auth/youtube.readonly' }),
				redirect_uri: `${window.location.origin}/auth/callback`,
			},
		});
	};

	return (
		<button onClick={connect} className="px-3 py-2 rounded-md bg-blue-600 text-white hover:bg-blue-700">
			{user ? 'Reconnect YouTube' : 'Connect YouTube'}
		</button>
	);
} 