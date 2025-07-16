import { useState, useEffect } from 'react';
import { useAuth } from '../contexts/AuthContext';

interface ABTest {
  id: number;
  video_id: string;
  video_title: string;
  title_variants: string[];
  current_variant_index: number;
  test_duration_hours: number;
  rotation_interval_hours: number;
  status: string;
  created_at: string;
  started_at?: string;
  completed_at?: string;
}

interface TestListProps {
  refreshTrigger: number;
}

export function TestList({ refreshTrigger }: TestListProps) {
  const { getAuthToken } = useAuth();
  const [tests, setTests] = useState<ABTest[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');

  const fetchTests = async () => {
    try {
      const token = await getAuthToken();
      const apiUrl = (import.meta as any).env.VITE_API_URL || 'http://localhost:8000';

      const response = await fetch(`${apiUrl}/api/ab-tests/`, {
        headers: {
          'Authorization': `Bearer ${token}`,
        },
      });

      if (!response.ok) {
        throw new Error('Failed to fetch tests');
      }

      const data = await response.json();
      setTests(data);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to fetch tests');
    } finally {
      setLoading(false);
    }
  };

  const startTest = async (testId: number) => {
    try {
      const token = await getAuthToken();
      const apiUrl = (import.meta as any).env.VITE_API_URL || 'http://localhost:8000';

      const response = await fetch(`${apiUrl}/api/ab-tests/${testId}/start`, {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${token}`,
        },
      });

      if (!response.ok) {
        throw new Error('Failed to start test');
      }

      fetchTests();
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to start test');
    }
  };

  const stopTest = async (testId: number) => {
    try {
      const token = await getAuthToken();
      const apiUrl = (import.meta as any).env.VITE_API_URL || 'http://localhost:8000';

      const response = await fetch(`${apiUrl}/api/ab-tests/${testId}/stop`, {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${token}`,
        },
      });

      if (!response.ok) {
        throw new Error('Failed to stop test');
      }

      fetchTests();
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to stop test');
    }
  };

  const deleteTest = async (testId: number) => {
    if (!confirm('Are you sure you want to delete this test?')) {
      return;
    }

    try {
      const token = await getAuthToken();
      const apiUrl = (import.meta as any).env.VITE_API_URL || 'http://localhost:8000';

      const response = await fetch(`${apiUrl}/api/ab-tests/${testId}`, {
        method: 'DELETE',
        headers: {
          'Authorization': `Bearer ${token}`,
        },
      });

      if (!response.ok) {
        throw new Error('Failed to delete test');
      }

      fetchTests();
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to delete test');
    }
  };

  useEffect(() => {
    fetchTests();
  }, [refreshTrigger]);

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'active': return 'bg-green-100 text-green-800';
      case 'completed': return 'bg-blue-100 text-blue-800';
      case 'stopped': return 'bg-red-100 text-red-800';
      default: return 'bg-gray-100 text-gray-800';
    }
  };

  const formatDate = (dateString: string) => {
    return new Date(dateString).toLocaleDateString('en-US', {
      year: 'numeric',
      month: 'short',
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit'
    });
  };

  if (loading) {
    return (
      <div className="flex justify-center items-center py-8">
        <div className="text-gray-500">Loading tests...</div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="bg-red-50 border border-red-200 rounded-md p-4">
        <div className="text-red-800">{error}</div>
        <button
          onClick={fetchTests}
          className="mt-2 text-red-600 hover:text-red-800 text-sm"
        >
          Try again
        </button>
      </div>
    );
  }

  if (tests.length === 0) {
    return (
      <div className="text-center py-8">
        <div className="text-gray-500 mb-2">No tests created yet</div>
        <div className="text-sm text-gray-400">Create your first A/B test to get started</div>
      </div>
    );
  }

  return (
    <div className="space-y-4">
      {tests.map((test) => (
        <div key={test.id} className="bg-white border border-gray-200 rounded-lg p-4">
          <div className="flex justify-between items-start mb-3">
            <div>
              <h3 className="font-medium text-gray-900 mb-1">{test.video_title}</h3>
              <div className="text-sm text-gray-500">
                Video ID: {test.video_id} • Created: {formatDate(test.created_at)}
              </div>
            </div>
            <span className={`px-2 py-1 rounded-full text-xs font-medium ${getStatusColor(test.status)}`}>
              {test.status}
            </span>
          </div>

          <div className="mb-3">
            <div className="text-sm font-medium text-gray-700 mb-1">Title Variants:</div>
            <div className="space-y-1">
              {test.title_variants.map((variant, index) => (
                <div
                  key={index}
                  className={`text-sm p-2 rounded ${
                    index === test.current_variant_index && test.status === 'active'
                      ? 'bg-blue-50 border border-blue-200'
                      : 'bg-gray-50'
                  }`}
                >
                  {index === test.current_variant_index && test.status === 'active' && (
                    <span className="text-blue-600 font-medium">ACTIVE: </span>
                  )}
                  {variant}
                </div>
              ))}
            </div>
          </div>

          <div className="flex justify-between items-center text-sm text-gray-600 mb-3">
            <span>Duration: {test.test_duration_hours}h</span>
            <span>Rotation: {test.rotation_interval_hours}h</span>
            {test.started_at && (
              <span>Started: {formatDate(test.started_at)}</span>
            )}
          </div>

          <div className="flex gap-2">
            {test.status === 'draft' && (
              <button
                onClick={() => startTest(test.id)}
                className="px-3 py-1 bg-green-600 text-white text-sm rounded hover:bg-green-700"
              >
                Start Test
              </button>
            )}
            {test.status === 'active' && (
              <button
                onClick={() => stopTest(test.id)}
                className="px-3 py-1 bg-red-600 text-white text-sm rounded hover:bg-red-700"
              >
                Stop Test
              </button>
            )}
            {test.status !== 'active' && (
              <button
                onClick={() => deleteTest(test.id)}
                className="px-3 py-1 bg-gray-600 text-white text-sm rounded hover:bg-gray-700"
              >
                Delete
              </button>
            )}
          </div>
        </div>
      ))}
    </div>
  );
}
