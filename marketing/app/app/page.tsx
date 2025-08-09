'use client'

import { useEffect, useState } from 'react'

// API configuration
const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'

// Simple API client
class ApiClient {
  private async getAuthToken(): Promise<string | null> {
    // For now, we'll need to implement Firebase auth
    return null
  }

  private async fetchWithAuth(url: string, options: RequestInit = {}) {
    const token = await this.getAuthToken()
    
    const headers = {
      'Content-Type': 'application/json',
      ...(token ? { Authorization: `Bearer ${token}` } : {}),
      ...options.headers,
    }

    const response = await fetch(`${API_BASE_URL}${url}`, {
      ...options,
      headers,
    })

    if (!response.ok) {
      const error = await response.json().catch(() => ({ detail: 'Network error' }))
      throw new Error(error.detail || `HTTP error! status: ${response.status}`)
    }

    return response.json()
  }

  async healthCheck() {
    const response = await fetch(`${API_BASE_URL}/health`)
    return response.json()
  }
}

const apiClient = new ApiClient()

export default function AppDashboard() {
  const [health, setHealth] = useState<any>(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    const checkHealth = async () => {
      try {
        const result = await apiClient.healthCheck()
        setHealth(result)
      } catch (err) {
        setError(err instanceof Error ? err.message : 'Failed to connect to API')
      } finally {
        setLoading(false)
      }
    }

    checkHealth()
  }, [])

  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto"></div>
          <p className="mt-4 text-gray-600">Loading TitleTesterPro...</p>
        </div>
      </div>
    )
  }

  if (error) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="text-center">
          <div className="text-red-500 text-xl mb-4">⚠️ Connection Error</div>
          <p className="text-gray-600 mb-4">{error}</p>
          <button 
            onClick={() => window.location.reload()} 
            className="bg-blue-600 text-white px-4 py-2 rounded hover:bg-blue-700"
          >
            Retry
          </button>
        </div>
      </div>
    )
  }

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <nav className="bg-white shadow-sm">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between h-16">
            <div className="flex items-center">
              <h1 className="text-xl font-semibold text-gray-900">TitleTesterPro Dashboard</h1>
            </div>
            <div className="flex items-center space-x-4">
              <span className="text-sm text-gray-500">API Status: {health?.status}</span>
            </div>
          </div>
        </div>
      </nav>

      {/* Main Content */}
      <main className="max-w-7xl mx-auto py-6 sm:px-6 lg:px-8">
        <div className="px-4 py-6 sm:px-0">
          <div className="border-4 border-dashed border-gray-200 rounded-lg h-96 flex items-center justify-center">
            <div className="text-center">
              <h2 className="text-2xl font-bold text-gray-900 mb-4">Welcome to TitleTesterPro</h2>
              <p className="text-gray-600 mb-6">Your dashboard is successfully running at /app</p>
              <div className="bg-green-50 border border-green-200 rounded-lg p-4 mb-4">
                <p className="text-green-800">✅ API Connection: {health?.status}</p>
                <p className="text-green-800">✅ Service: {health?.service}</p>
                <p className="text-green-800">✅ Path: titletesterpro.com/app</p>
              </div>
              
              {/* Navigation Links */}
              <div className="space-y-2">
                <a 
                  href="/app/channels" 
                  className="block bg-blue-600 text-white px-4 py-2 rounded hover:bg-blue-700 transition-colors"
                >
                  Manage Channels
                </a>
                <a 
                  href="/app/tests" 
                  className="block bg-green-600 text-white px-4 py-2 rounded hover:bg-green-700 transition-colors"
                >
                  A/B Tests
                </a>
                <a 
                  href="/app/billing" 
                  className="block bg-purple-600 text-white px-4 py-2 rounded hover:bg-purple-700 transition-colors"
                >
                  Billing
                </a>
              </div>
            </div>
          </div>
        </div>
      </main>
    </div>
  )
}