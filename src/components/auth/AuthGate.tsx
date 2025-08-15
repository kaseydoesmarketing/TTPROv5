import { useAuth0 } from '@auth0/auth0-react'
import { useEffect } from 'react'

export default function AuthGate() {
  const { isAuthenticated, isLoading, getIdTokenClaims } = useAuth0()
  
  useEffect(() => {
    const initializeSession = async () => {
      if (!isAuthenticated) return
      
      try {
        const claims = await getIdTokenClaims()
        const idToken = (claims as any)?.__raw
        if (!idToken) return
        
        const response = await fetch(`${import.meta.env.VITE_API_BASE_URL}/api/auth/login`, {
          method: 'POST',
          headers: { 
            'Authorization': `Bearer ${idToken}`,
            'Content-Type': 'application/json'
          },
          credentials: 'include',
        })
        
        if (response.ok) {
          // ensure we land on /app
          if (window.location.pathname !== '/app') {
            window.history.replaceState({}, document.title, '/app')
          }
        } else {
          console.error('Failed to initialize session:', response.status)
        }
      } catch (error) {
        console.error('Error initializing session:', error)
      }
    }
    
    if (!isLoading) {
      void initializeSession()
    }
  }, [isAuthenticated, isLoading, getIdTokenClaims])
  
  return null
}