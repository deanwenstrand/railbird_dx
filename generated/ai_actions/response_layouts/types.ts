export interface ResponseLayoutProps {
  actionId: string;
  inputs: Record<string, any>;
  context: Record<string, any>;
  result?: any;
  layoutType: 'approval' | 'display' | 'interactive';
  message?: string;
  onResponse?: (response: ResponseLayoutResponse) => void;
  isLoading?: boolean;
  metadata?: {
    user: any;
    permissions: string[];
    timestamp: string;
  };
}

export interface ResponseLayoutResponse {
  approved?: boolean;
  data_updates?: Record<string, any>;
  user_input?: Record<string, any>;
  custom_response?: any;
}
