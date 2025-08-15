import { Auth0ContextProvider, useAuthContext } from './contexts/Auth0Context';
import AuthGate from './components/auth/AuthGate';
import { LoginPage } from './components/LoginPage';
import { LandingPage } from './components/LandingPage';
import { Dashboard } from './components/Dashboard';
import { useState, useEffect } from 'react';
import './App.css';

function AppContent() {
  const { user, loading, login } = useAuthContext();
  const [showLogin, setShowLogin] = useState(false);
  const [apiHealthy, setApiHealthy] = useState<boolean | null>(null);

  // Check API health on mount
  useEffect(() => {
    const checkHealth = async () => {
      try {
        const response = await fetch(`${import.meta.env.VITE_API_BASE_URL}/api/healthz`, {
          credentials: 'include',
        });
        setApiHealthy(response.ok);
        if (response.ok) {
          console.log('API OK');
        }
      } catch (error) {
        console.error('API health check failed:', error);
        setApiHealthy(false);
      }
    };
    void checkHealth();
  }, []);

  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="animate-spin rounded-full h-32 w-32 border-b-2 border-gray-900"></div>
      </div>
    );
  }

  if (user) {
    return (
      <>
        {apiHealthy !== null && (
          <div className={`fixed top-2 right-2 px-2 py-1 text-xs rounded ${apiHealthy ? 'bg-green-100 text-green-800' : 'bg-red-100 text-red-800'}`}>
            API: {apiHealthy ? 'OK' : 'Down'}
          </div>
        )}
        <Dashboard />
      </>
    );
  }

  if (showLogin) {
    return <LoginPage onLogin={login} />;
  }

  return <LandingPage onGetStarted={() => setShowLogin(true)} />;
}

function App() {
  return (
    <Auth0ContextProvider>
      <AuthGate />
      <AppContent />
    </Auth0ContextProvider>
  );
}

export default App;
