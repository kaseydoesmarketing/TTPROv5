'use client'

export default function ChannelsPage() {
  return (
    <div className="min-h-screen bg-gray-50">
      <nav className="bg-white shadow-sm">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between h-16">
            <div className="flex items-center">
              <a href="/app" className="text-blue-600 hover:text-blue-800 mr-4">← Back to Dashboard</a>
              <h1 className="text-xl font-semibold text-gray-900">Channels</h1>
            </div>
          </div>
        </div>
      </nav>

      <main className="max-w-7xl mx-auto py-6 sm:px-6 lg:px-8">
        <div className="px-4 py-6 sm:px-0">
          <div className="bg-white shadow rounded-lg p-6">
            <h2 className="text-lg font-semibold mb-4">YouTube Channels</h2>
            <p className="text-gray-600 mb-4">Manage your connected YouTube channels here.</p>
            <div className="border-dashed border-2 border-gray-300 rounded-lg p-8 text-center">
              <p className="text-gray-500">Channel management functionality will be implemented here</p>
              <p className="text-sm text-gray-400 mt-2">Path: /app/channels</p>
            </div>
          </div>
        </div>
      </main>
    </div>
  )
}