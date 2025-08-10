'use client';

import { useEffect, useState, Suspense } from 'react';
import { useRouter, useSearchParams } from 'next/navigation';

function OAuth2CallbackContent() {
  const router = useRouter();
  const searchParams = useSearchParams();
  const [status, setStatus] = useState<'processing' | 'success' | 'error'>('processing');
  const [message, setMessage] = useState('Processing OAuth callback...');

  useEffect(() => {
    const handleCallback = async () => {
      try {
        const code = searchParams?.get('code');
        const error = searchParams?.get('error');
        
        if (error) {
          setStatus('error');
          setMessage(`OAuth error: ${error}`);
          setTimeout(() => router.push('/app'), 3000);
          return;
        }
        
        if (!code) {
          setStatus('error');
          setMessage('No authorization code received');
          setTimeout(() => router.push('/app'), 3000);
          return;
        }
        
        // Exchange code for tokens
        const apiBaseUrl = process.env.NEXT_PUBLIC_API_BASE_URL || 'https://ttprov4-k58o.onrender.com';
        
        const response = await fetch(`${apiBaseUrl}/api/auth/google/exchange`, {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
          },
          credentials: 'include',
          body: JSON.stringify({ code })
        });
        
        if (response.ok) {
          const result = await response.json();
          setStatus('success');
          setMessage('YouTube access granted! Redirecting to dashboard...');
          setTimeout(() => router.push('/app'), 2000);
        } else {
          const error = await response.text();
          setStatus('error');
          setMessage(`Token exchange failed: ${error}`);
          setTimeout(() => router.push('/app'), 3000);
        }
        
      } catch (error) {
        console.error('OAuth callback error:', error);
        setStatus('error');
        setMessage(`Callback error: ${error}`);
        setTimeout(() => router.push('/app'), 3000);
      }
    };
    
    handleCallback();
  }, [searchParams, router]);
  
  return (
    <div className="min-h-screen flex items-center justify-center bg-gray-50">
      <div className="max-w-md w-full bg-white shadow-lg rounded-lg p-6 text-center">
        <div className="mb-4">
          {status === 'processing' && (
            <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto"></div>
          )}
          {status === 'success' && (
            <div className="rounded-full h-12 w-12 bg-green-100 mx-auto flex items-center justify-center">
              <svg className="h-6 w-6 text-green-600" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
              </svg>
            </div>
          )}
          {status === 'error' && (
            <div className="rounded-full h-12 w-12 bg-red-100 mx-auto flex items-center justify-center">
              <svg className="h-6 w-6 text-red-600" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
              </svg>
            </div>
          )}
        </div>
        
        <h2 className="text-xl font-semibold text-gray-900 mb-2">
          {status === 'processing' && 'Connecting YouTube...'}
          {status === 'success' && 'Success!'}
          {status === 'error' && 'Error'}
        </h2>
        
        <p className="text-gray-600">{message}</p>
      </div>
    </div>
  );
}

export default function OAuth2Callback() {
  return (
    <Suspense fallback={
      <div className="min-h-screen flex items-center justify-center bg-gray-50">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto"></div>
      </div>
    }>
      <OAuth2CallbackContent />
    </Suspense>
  );
}