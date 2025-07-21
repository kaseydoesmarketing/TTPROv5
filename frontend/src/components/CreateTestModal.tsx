import React, { useState } from 'react';
import { useAuth } from '../contexts/AuthContext';
import { VideoSelector } from './VideoSelector';
import { DateTimePicker } from './DateTimePicker';

interface CreateTestModalProps {
  isOpen: boolean;
  onClose: () => void;
  onTestCreated: () => void;
}

export function CreateTestModal({ isOpen, onClose, onTestCreated }: CreateTestModalProps) {
  const { getAuthToken } = useAuth();
  const [formData, setFormData] = useState({
    videoId: '',
    videoTitle: '',
    titleVariants: ['', ''],
    startTime: undefined as Date | undefined,
    endTime: undefined as Date | undefined,
    rotationIntervalHours: 4
  });
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  const addTitleVariant = () => {
    if (formData.titleVariants.length < 5) {
      setFormData({
        ...formData,
        titleVariants: [...formData.titleVariants, '']
      });
    }
  };

  const removeTitleVariant = (index: number) => {
    if (formData.titleVariants.length > 2) {
      const newVariants = formData.titleVariants.filter((_, i) => i !== index);
      setFormData({
        ...formData,
        titleVariants: newVariants
      });
    }
  };

  const updateTitleVariant = (index: number, value: string) => {
    const newVariants = [...formData.titleVariants];
    newVariants[index] = value;
    setFormData({
      ...formData,
      titleVariants: newVariants
    });
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    setError('');

    try {
      const token = await getAuthToken();
      const apiUrl = (import.meta as any).env.VITE_API_URL || 'http://localhost:8000';

      const response = await fetch(`${apiUrl}/api/ab-tests/`, {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          video_id: formData.videoId,
          title_variants: formData.titleVariants.filter(variant => variant.trim() !== ''),
          test_duration_hours: formData.startTime && formData.endTime 
            ? Math.ceil((formData.endTime.getTime() - formData.startTime.getTime()) / (1000 * 60 * 60))
            : 24,
          rotation_interval_hours: formData.rotationIntervalHours,
          start_time: formData.startTime?.toISOString(),
          end_time: formData.endTime?.toISOString()
        }),
      });

      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.detail || 'Failed to create test');
      }

      onTestCreated();
      onClose();
      setFormData({
        videoId: '',
        videoTitle: '',
        titleVariants: ['', ''],
        startTime: undefined,
        endTime: undefined,
        rotationIntervalHours: 4
      });
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to create test');
    } finally {
      setLoading(false);
    }
  };

  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
      <div className="bg-white rounded-lg p-6 w-full max-w-md max-h-[90vh] overflow-y-auto">
        <div className="flex justify-between items-center mb-4">
          <h2 className="text-xl font-bold">Create A/B Test</h2>
          <button
            onClick={onClose}
            className="text-gray-500 hover:text-gray-700"
          >
            ✕
          </button>
        </div>

        <form onSubmit={handleSubmit} className="space-y-4">
          <VideoSelector
            selectedVideoId={formData.videoId}
            onVideoSelect={(videoId, videoTitle) => {
              setFormData({ ...formData, videoId, videoTitle });
            }}
          />

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Title Variants (2-5 required)
            </label>
            {formData.titleVariants.map((variant, index) => (
              <div key={index} className="flex gap-2 mb-2">
                <input
                  type="text"
                  value={variant}
                  onChange={(e) => updateTitleVariant(index, e.target.value)}
                  placeholder={`Title variant ${index + 1}`}
                  className="flex-1 px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                  required
                />
                {formData.titleVariants.length > 2 && (
                  <button
                    type="button"
                    onClick={() => removeTitleVariant(index)}
                    className="px-2 py-2 text-red-600 hover:text-red-800"
                  >
                    ✕
                  </button>
                )}
              </div>
            ))}
            {formData.titleVariants.length < 5 && (
              <button
                type="button"
                onClick={addTitleVariant}
                className="text-blue-600 hover:text-blue-800 text-sm"
              >
                + Add another variant
              </button>
            )}
          </div>

          <div className="grid grid-cols-2 gap-4">
            <DateTimePicker
              label="Start Time"
              value={formData.startTime}
              onChange={(date) => setFormData({ ...formData, startTime: date })}
              minDate={new Date()}
            />
            <DateTimePicker
              label="End Time"
              value={formData.endTime}
              onChange={(date) => setFormData({ ...formData, endTime: date })}
              minDate={formData.startTime || new Date()}
            />
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Rotation Interval (hours)
            </label>
            <input
              type="number"
              min="1"
              max="24"
              value={formData.rotationIntervalHours}
              onChange={(e) => setFormData({ ...formData, rotationIntervalHours: parseInt(e.target.value) })}
              className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
              required
            />
            <p className="text-xs text-gray-500 mt-1">
              How often to rotate between title variants during the test
            </p>
          </div>

          {formData.startTime && formData.endTime && (
            <div className="bg-blue-50 p-3 rounded-md">
              <p className="text-sm text-blue-800">
                <strong>Test Duration:</strong> {Math.ceil((formData.endTime.getTime() - formData.startTime.getTime()) / (1000 * 60 * 60))} hours
              </p>
            </div>
          )}

          {error && (
            <div className="text-red-600 text-sm bg-red-50 p-2 rounded">
              {error}
            </div>
          )}

          <div className="flex gap-3 pt-4">
            <button
              type="button"
              onClick={onClose}
              className="flex-1 px-4 py-2 text-gray-700 bg-gray-100 rounded-md hover:bg-gray-200"
            >
              Cancel
            </button>
            <button
              type="submit"
              disabled={loading}
              className="flex-1 px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700 disabled:opacity-50"
            >
              {loading ? 'Creating...' : 'Create Test'}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
}
