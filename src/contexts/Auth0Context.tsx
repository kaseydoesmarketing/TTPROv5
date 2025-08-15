import { createContext, useContext, useEffect, useState, useCallback, ReactNode } from 'react'
import { useAuth0 } from '@auth0/auth0-react'

interface User {
  id: string
  email: string
  name?: string
  picture?: string
  email_verified?: boolean
}

interface AuthContextType {
  user: User | null
  loading: boolean
  error: Error | null
  login: () => Promise<void>
  logout: () => Promise<void>
  getSessionToken: () => Promise<string | null>
}

const AuthContext = createContext<AuthContextType | undefined>(undefined)

export function useAuthContext() {
  const context = useContext(AuthContext)
  if (context === undefined) {
    throw new Error('useAuthContext must be used within an Auth0ContextProvider')
  }
  return context
}

interface Auth0ContextProviderProps {
  children: ReactNode
}

export function Auth0ContextProvider({ children }: Auth0ContextProviderProps) {
  const {
    user: auth0User,
    isAuthenticated,
    isLoading,
    error: auth0Error,
    loginWithRedirect,
    logout: auth0Logout,
    getIdTokenClaims,
  } = useAuth0()

  const [user, setUser] = useState<User | null>(null)
  const [sessionInitialized, setSessionInitialized] = useState(false)
  const [error, setError] = useState<Error | null>(null)

  // Initialize session with backend when authenticated
  useEffect(() => {
    const initializeSession = async () => {
      if (!isAuthenticated || sessionInitialized) return

      try {
        const claims = await getIdTokenClaims()
        const idToken = (claims as any)?.__raw
        
        if (!idToken) {
          throw new Error('No ID token available')
        }

        const response = await fetch(`${import.meta.env.VITE_API_BASE_URL}/api/auth/login`, {
          method: 'POST',
          headers: {
            'Authorization': `Bearer ${idToken}`,
            'Content-Type': 'application/json',
          },
          credentials: 'include',
        })

        if (!response.ok) {
          throw new Error(`Session initialization failed: ${response.status}`)
        }

        const data = await response.json()
        
        // Set user from Auth0 data
        if (auth0User) {
          setUser({
            id: auth0User.sub || '',
            email: auth0User.email || '',
            name: auth0User.name,
            picture: auth0User.picture,
            email_verified: auth0User.email_verified,
          })
        }
        
        setSessionInitialized(true)
        console.log('Session initialized successfully', data)
      } catch (err) {
        console.error('Failed to initialize session:', err)
        setError(err as Error)
      }
    }

    if (!isLoading) {
      void initializeSession()
    }
  }, [isAuthenticated, isLoading, sessionInitialized, getIdTokenClaims, auth0User])

  // Update user when auth0User changes
  useEffect(() => {
    if (isAuthenticated && auth0User) {
      setUser({
        id: auth0User.sub || '',
        email: auth0User.email || '',
        name: auth0User.name,
        picture: auth0User.picture,
        email_verified: auth0User.email_verified,
      })
    } else if (!isAuthenticated) {
      setUser(null)
      setSessionInitialized(false)
    }
  }, [isAuthenticated, auth0User])

  const login = useCallback(async () => {
    await loginWithRedirect()
  }, [loginWithRedirect])

  const logout = useCallback(async () => {
    // Call backend logout endpoint to clear session
    try {
      await fetch(`${import.meta.env.VITE_API_BASE_URL}/api/auth/logout`, {
        method: 'POST',
        credentials: 'include',
      })
    } catch (err) {
      console.error('Backend logout failed:', err)
    }
    
    // Logout from Auth0
    auth0Logout({
      logoutParams: {
        returnTo: window.location.origin,
      },
    })
    
    setUser(null)
    setSessionInitialized(false)
  }, [auth0Logout])

  const getSessionToken = useCallback(async (): Promise<string | null> => {
    if (!isAuthenticated) return null
    
    try {
      const claims = await getIdTokenClaims()
      return (claims as any)?.__raw || null
    } catch (err) {
      console.error('Failed to get session token:', err)
      return null
    }
  }, [isAuthenticated, getIdTokenClaims])

  const value: AuthContextType = {
    user,
    loading: isLoading,
    error: error || auth0Error || null,
    login,
    logout,
    getSessionToken,
  }

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>
}