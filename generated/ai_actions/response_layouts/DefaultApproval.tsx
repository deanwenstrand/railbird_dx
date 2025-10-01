import React from 'react';
import { ResponseLayoutProps } from './types';

export function DefaultApproval(props: ResponseLayoutProps) {
  return (
    <div className="border border-stone-200 bg-white rounded-lg p-4">
      <div className="text-center text-stone-500">
        Basic approval layout with approve/reject buttons
      </div>
    </div>
  );
}
