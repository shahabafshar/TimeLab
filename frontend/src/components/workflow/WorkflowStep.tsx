"use client";

import React from "react";

interface WorkflowStepProps {
  title: string;
  description?: string;
  children: React.ReactNode;
}

export function WorkflowStep({ title, description, children }: WorkflowStepProps) {
  return (
    <div className="space-y-4">
      <div>
        <h2 className="text-2xl font-bold">{title}</h2>
        {description && <p className="text-gray-600 mt-2">{description}</p>}
      </div>
      <div>{children}</div>
    </div>
  );
}

