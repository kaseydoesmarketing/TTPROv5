'use client'

import { useEffect, useState } from 'react';

interface AuthGateProps {
	children: React.ReactNode;
}

export default function AuthGate({ children }: AuthGateProps) {
	const [ready, setReady] = useState(false);

	useEffect(() => {
		setReady(true);
	}, []);

	if (!ready) {
		return (
			<div className="min-h-screen flex items-center justify-center bg-gray-50">
				<div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600"></div>
			</div>
		);
	}

	return <>{children}</>;
}