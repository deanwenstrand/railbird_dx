import React from 'react';
import { ResponseLayoutProps } from './types';

export function DefaultInteractive(props: ResponseLayoutProps) {
  return (
    <div className="border border-stone-200 bg-white rounded-lg p-4">
      <div className="text-center text-stone-500">
        Interactive layout for user input
      </div>
    </div>
  );
}
