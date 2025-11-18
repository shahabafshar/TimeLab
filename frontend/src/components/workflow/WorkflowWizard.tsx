"use client";

import React, { useState } from "react";

interface WorkflowStep {
  id: string;
  title: string;
  component: React.ReactNode;
}

interface WorkflowWizardProps {
  steps: WorkflowStep[];
  onComplete: () => void;
}

export function WorkflowWizard({ steps, onComplete }: WorkflowWizardProps) {
  const [currentStep, setCurrentStep] = useState(0);

  const nextStep = () => {
    if (currentStep < steps.length - 1) {
      setCurrentStep(currentStep + 1);
    } else {
      onComplete();
    }
  };

  const prevStep = () => {
    if (currentStep > 0) {
      setCurrentStep(currentStep - 1);
    }
  };

  return (
    <div className="w-full max-w-4xl mx-auto">
      {/* Progress indicator */}
      <div className="mb-8">
        <div className="flex justify-between mb-2">
          {steps.map((step, idx) => (
            <div
              key={step.id}
              className={`flex-1 text-center ${
                idx <= currentStep ? "text-green-600" : "text-gray-400"
              }`}
            >
              <div
                className={`w-8 h-8 rounded-full mx-auto mb-2 flex items-center justify-center ${
                  idx <= currentStep
                    ? "bg-green-600 text-white"
                    : "bg-gray-200 text-gray-600"
                }`}
              >
                {idx + 1}
              </div>
              <div className="text-xs">{step.title}</div>
            </div>
          ))}
        </div>
        <div className="w-full bg-gray-200 h-1">
          <div
            className="bg-green-600 h-1 transition-all"
            style={{ width: `${((currentStep + 1) / steps.length) * 100}%` }}
          />
        </div>
      </div>

      {/* Current step content */}
      <div className="bg-white p-6 rounded-lg border">
        {steps[currentStep].component}
      </div>

      {/* Navigation */}
      <div className="flex justify-between mt-6">
        <button
          onClick={prevStep}
          disabled={currentStep === 0}
          className="px-6 py-2 border rounded-md disabled:opacity-50 disabled:cursor-not-allowed"
        >
          Previous
        </button>
        <button
          onClick={nextStep}
          className="px-6 py-2 bg-green-600 text-white rounded-md hover:bg-green-700"
        >
          {currentStep === steps.length - 1 ? "Complete" : "Next"}
        </button>
      </div>
    </div>
  );
}

