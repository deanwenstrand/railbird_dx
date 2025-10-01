import React from 'react';
import { ResponseLayoutProps, ResponseLayoutResponse } from './types';

// Dynamic imports for code splitting


// Component registry - duck-typed by action_id
const LAYOUT_COMPONENTS = {

} as const;

// Fallback components
import { DefaultDisplay } from './DefaultDisplay';
import { DefaultApproval } from './DefaultApproval'; 
import { DefaultInteractive } from './DefaultInteractive';

export interface ResponseLayoutRegistryProps extends ResponseLayoutProps {}

export function ResponseLayoutRegistry(props: ResponseLayoutRegistryProps) {
  const { actionId, layoutType } = props;
  
  // Try custom layout first (duck-typing)
  const CustomLayout = LAYOUT_COMPONENTS[actionId as keyof typeof LAYOUT_COMPONENTS];
  
  if (CustomLayout) {
    return (
      <React.Suspense fallback={<div className="animate-pulse">Loading layout...</div>}>
        <CustomLayout {...props} />
      </React.Suspense>
    );
  }
  
  // Fallback to defaults by type
  switch (layoutType) {
    case 'approval':
      return <DefaultApproval {...props} />;
    case 'interactive': 
      return <DefaultInteractive {...props} />;
    case 'display':
    default:
      return <DefaultDisplay {...props} />;
  }
}

// Export registry for debugging
export const availableLayouts = Object.keys(LAYOUT_COMPONENTS);
