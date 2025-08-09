'use client'

import { useState } from 'react';
import { mutate } from 'swr';
import { Button } from '@/components/ui/button';
import Modal from '@/components/ui/Modal';
import YouTubePicker from '@/components/YouTubePicker';
import { createCampaign } from '@/lib/api';

interface NewCampaignWizardProps {
  isOpen: boolean;
  onClose: () => void;
}

interface FormData {
  channelId: string;
  videoIds: string[];
  titles: string[];
  intervalMinutes: number;
  durationHours: number;
}

export default function NewCampaignWizard({ isOpen, onClose }: NewCampaignWizardProps) {
  const [currentStep, setCurrentStep] = useState(1);
  const [isCreating, setIsCreating] = useState(false);
  const [error, setError] = useState<string | null>(null);
  
  const [formData, setFormData] = useState<FormData>({
    channelId: '',
    videoIds: [],
    titles: [''],
    intervalMinutes: 60,
    durationHours: 24,
  });

  const handleClose = () => {
    if (!isCreating) {
      setCurrentStep(1);
      setFormData({
        channelId: '',
        videoIds: [],
        titles: [''],
        intervalMinutes: 60,
        durationHours: 24,
      });
      setError(null);
      onClose();
    }
  };

  const handleYouTubeSelection = (selection: { channelId: string; videoIds: string[] }) => {
    setFormData(prev => ({
      ...prev,
      channelId: selection.channelId,
      videoIds: selection.videoIds
    }));
  };

  const addTitleVariant = () => {
    if (formData.titles.length < 5) {
      setFormData(prev => ({
        ...prev,
        titles: [...prev.titles, '']
      }));
    }
  };

  const removeTitleVariant = (index: number) => {
    if (formData.titles.length > 1) {
      setFormData(prev => ({
        ...prev,
        titles: prev.titles.filter((_, i) => i !== index)
      }));
    }
  };

  const updateTitle = (index: number, value: string) => {
    setFormData(prev => ({
      ...prev,
      titles: prev.titles.map((title, i) => i === index ? value : title)
    }));
  };

  const canProceedFromStep1 = formData.channelId && formData.videoIds.length > 0;
  const canProceedFromStep2 = formData.titles.every(title => title.trim().length > 0);

  const handleNextStep = () => {
    if (currentStep < 3) {
      setCurrentStep(prev => prev + 1);
      setError(null);
    }
  };

  const handlePrevStep = () => {
    if (currentStep > 1) {
      setCurrentStep(prev => prev - 1);
      setError(null);
    }
  };

  const handleCreateCampaign = async () => {
    setIsCreating(true);
    setError(null);

    try {
      await createCampaign(formData);
      await mutate('campaigns');
      handleClose();
    } catch (error) {
      setError(error instanceof Error ? error.message : 'Failed to create campaign');
    } finally {
      setIsCreating(false);
    }
  };

  const renderStep = () => {
    switch (currentStep) {
      case 1:
        return (
          <div className="space-y-4">
            <div className="text-center mb-6">
              <h3 className="text-xl font-semibold text-slate-900 mb-2">Select Content</h3>
              <p className="text-slate-600">Choose your YouTube channel and videos to test</p>
            </div>
            <YouTubePicker onSelectionChange={handleYouTubeSelection} />
          </div>
        );

      case 2:
        return (
          <div className="space-y-4">
            <div className="text-center mb-6">
              <h3 className="text-xl font-semibold text-slate-900 mb-2">Title Variants</h3>
              <p className="text-slate-600">Create 1-5 title variations to test</p>
            </div>

            <div className="space-y-3">
              {formData.titles.map((title, index) => (
                <div key={index} className="flex items-center space-x-3">
                  <div className="flex-1">
                    <label className="block text-sm font-medium text-slate-700 mb-1">
                      Title {index + 1}
                    </label>
                    <input
                      type="text"
                      value={title}
                      onChange={(e) => updateTitle(index, e.target.value)}
                      placeholder={`Enter title variant ${index + 1}`}
                      className="w-full px-3 py-2 border border-slate-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                    />
                  </div>
                  {formData.titles.length > 1 && (
                    <button
                      type="button"
                      onClick={() => removeTitleVariant(index)}
                      className="mt-6 p-2 text-red-500 hover:text-red-700"
                    >
                      <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16" />
                      </svg>
                    </button>
                  )}
                </div>
              ))}
            </div>

            {formData.titles.length < 5 && (
              <button
                type="button"
                onClick={addTitleVariant}
                className="w-full px-4 py-2 border-2 border-dashed border-slate-300 rounded-lg text-slate-600 hover:border-slate-400 hover:text-slate-700 transition-colors"
              >
                + Add Title Variant ({formData.titles.length}/5)
              </button>
            )}
          </div>
        );

      case 3:
        return (
          <div className="space-y-6">
            <div className="text-center mb-6">
              <h3 className="text-xl font-semibold text-slate-900 mb-2">Schedule Settings</h3>
              <p className="text-slate-600">Configure rotation interval and campaign duration</p>
            </div>

            <div className="grid grid-cols-2 gap-6">
              <div>
                <label className="block text-sm font-medium text-slate-700 mb-2">
                  Rotation Interval
                </label>
                <select
                  value={formData.intervalMinutes}
                  onChange={(e) => setFormData(prev => ({ ...prev, intervalMinutes: parseInt(e.target.value) }))}
                  className="w-full px-3 py-2 border border-slate-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                >
                  <option value={30}>Every 30 minutes</option>
                  <option value={60}>Every hour</option>
                  <option value={120}>Every 2 hours</option>
                </select>
              </div>

              <div>
                <label className="block text-sm font-medium text-slate-700 mb-2">
                  Campaign Duration
                </label>
                <select
                  value={formData.durationHours}
                  onChange={(e) => setFormData(prev => ({ ...prev, durationHours: parseInt(e.target.value) }))}
                  className="w-full px-3 py-2 border border-slate-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                >
                  <option value={24}>24 hours</option>
                  <option value={48}>48 hours</option>
                  <option value={72}>72 hours</option>
                </select>
              </div>
            </div>

            {/* Campaign Summary */}
            <div className="bg-slate-50 rounded-lg p-4">
              <h4 className="font-medium text-slate-900 mb-2">Campaign Summary</h4>
              <div className="text-sm text-slate-600 space-y-1">
                <p>• {formData.videoIds.length} video(s) selected</p>
                <p>• {formData.titles.length} title variant(s)</p>
                <p>• Rotate every {formData.intervalMinutes} minutes</p>
                <p>• Run for {formData.durationHours} hours</p>
              </div>
            </div>
          </div>
        );

      default:
        return null;
    }
  };

  return (
    <Modal isOpen={isOpen} onClose={handleClose} title="Create New Campaign">
      <div className="min-h-[400px]">
        {/* Progress Bar */}
        <div className="flex items-center mb-8">
          {[1, 2, 3].map((step) => (
            <div key={step} className="flex items-center">
              <div className={`w-8 h-8 rounded-full flex items-center justify-center text-sm font-medium ${
                step <= currentStep 
                  ? 'bg-blue-600 text-white' 
                  : 'bg-slate-200 text-slate-500'
              }`}>
                {step}
              </div>
              {step < 3 && (
                <div className={`w-12 h-1 mx-2 ${
                  step < currentStep ? 'bg-blue-600' : 'bg-slate-200'
                }`} />
              )}
            </div>
          ))}
        </div>

        {/* Step Content */}
        <div className="mb-8">
          {renderStep()}
        </div>

        {/* Error Message */}
        {error && (
          <div className="mb-6 p-3 bg-red-50 border border-red-200 rounded-lg text-red-700 text-sm">
            {error}
          </div>
        )}

        {/* Actions */}
        <div className="flex justify-between">
          <div>
            {currentStep > 1 && (
              <Button variant="outline" onClick={handlePrevStep} disabled={isCreating}>
                Previous
              </Button>
            )}
          </div>
          
          <div className="space-x-2">
            <Button variant="outline" onClick={handleClose} disabled={isCreating}>
              Cancel
            </Button>
            
            {currentStep < 3 ? (
              <Button 
                onClick={handleNextStep}
                disabled={
                  (currentStep === 1 && !canProceedFromStep1) ||
                  (currentStep === 2 && !canProceedFromStep2)
                }
              >
                Next
              </Button>
            ) : (
              <Button onClick={handleCreateCampaign} disabled={isCreating}>
                {isCreating ? 'Creating...' : 'Create Campaign'}
              </Button>
            )}
          </div>
        </div>
      </div>
    </Modal>
  );
}