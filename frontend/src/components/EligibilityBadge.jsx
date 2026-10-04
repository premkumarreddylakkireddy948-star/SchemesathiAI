import React from 'react';
import { CheckCircle2, AlertTriangle, Info } from 'lucide-react';

export default function EligibilityBadge({ isPotentiallyEligible = true, label = '' }) {
  if (isPotentiallyEligible) {
    return (
      <span className="inline-flex items-center space-x-1.5 px-3 py-1 rounded-full text-xs font-semibold bg-emerald-50 text-emerald-700 border border-emerald-200">
        <CheckCircle2 className="w-3.5 h-3.5 text-emerald-600" />
        <span>{label || 'Potentially Relevant'}</span>
      </span>
    );
  }

  return (
    <span className="inline-flex items-center space-x-1.5 px-3 py-1 rounded-full text-xs font-semibold bg-amber-50 text-amber-700 border border-amber-200">
      <AlertTriangle className="w-3.5 h-3.5 text-amber-600" />
      <span>{label || 'Verification Required'}</span>
    </span>
  );
}
