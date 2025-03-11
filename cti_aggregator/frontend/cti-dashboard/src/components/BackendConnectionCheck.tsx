"use client"

import { useState, useEffect } from 'react'
import { Alert, AlertTitle, AlertDescription } from '@/components/ui/alert'
import { Button } from '@/components/ui/button'
import { RefreshCw, ServerOff } from 'lucide-react'

// Base API URL from environment variable with fallback
const API_BASE_URL = 
  typeof window !== 'undefined' && process.env.NEXT_PUBLIC_API_URL 
    ? process.env.NEXT_PUBLIC_API_URL 
    : 'http://localhost:8000/api';

export function BackendConnectionCheck() {
  const [connectionStatus, setConnectionStatus] = useState<'checking' | 'connected' | 'disconnected'>('checking');
  const [retrying, setRetrying] = useState(false);
  const [apiInfo, setApiInfo] = useState<any>(null);

  useEffect(() => {
    // Only run in browser
    if (typeof window !== 'undefined') {
      checkApiConnection();
    }
  }, []);

  const checkApiConnection = async () => {
    try {
      setConnectionStatus('checking');
      setRetrying(true);

      // Use a timeout to avoid waiting too long
      const controller = new AbortController();
      const timeoutId = setTimeout(() => controller.abort(), 3000);

      const response = await fetch(`${API_BASE_URL}/health-check/`, {
        method: 'HEAD',
        signal: controller.signal
      }).catch(() => null);

      clearTimeout(timeoutId);

      if (response && response.ok) {
        setConnectionStatus('connected');
        
        // Get more detailed API info
        try {
          const infoResponse = await fetch(`${API_BASE_URL}/health-check/`);
          if (infoResponse.ok) {
            const data = await infoResponse.json();
            setApiInfo(data);
          }
        } catch (error) {
          console.error("Error fetching API details:", error);
        }
      } else {
        setConnectionStatus('disconnected');
      }
    } catch (error) {
      console.error("API connection check failed:", error);
      setConnectionStatus('disconnected');
    } finally {
      setRetrying(false);
    }
  };

  const handleRetry = () => {
    checkApiConnection();
  };

  // Don't show anything if we're connected or still checking initially
  if (connectionStatus === 'connected' || (connectionStatus === 'checking' && !retrying)) {
    return null;
  }

  return (
    <Alert variant="destructive" className="mb-4">
      <ServerOff className="h-4 w-4" />
      <AlertTitle>Backend Connection Issue</AlertTitle>
      <AlertDescription>
        {connectionStatus === 'checking' ? (
          'Checking connection to the backend API...'
        ) : (
          <>
            Unable to connect to the backend API. This may affect data loading and refreshing.
            <div className="mt-3 flex items-center space-x-2">
              <div className="text-sm">
                <p>Possible reasons:</p>
                <ul className="list-disc pl-5 mt-1">
                  <li>The backend server is not running</li>
                  <li>The API URL is not correctly configured</li>
                  <li>Network connectivity issues</li>
                </ul>
              </div>
            </div>
            <div className="mt-2">
              <Button 
                variant="outline" 
                size="sm" 
                onClick={handleRetry} 
                disabled={retrying}
              >
                {retrying ? (
                  <>
                    <RefreshCw className="h-4 w-4 mr-2 animate-spin" />
                    Checking Connection...
                  </>
                ) : (
                  <>
                    <RefreshCw className="h-4 w-4 mr-2" />
                    Retry Connection
                  </>
                )}
              </Button>
            </div>
          </>
        )}
      </AlertDescription>
    </Alert>
  );
} 