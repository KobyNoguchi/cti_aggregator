import React from 'react';
import { IntelligenceFeed, CISAKev } from '@/components/intel';

export default function DashboardPage() {
  return (
    <div className="container mx-auto py-8">
      <h1 className="text-3xl font-bold mb-6 dark:text-white">Threat Intelligence Dashboard</h1>
      
      <div className="grid grid-cols-1 gap-8">
        {/* Intel Feed Section */}
        <div className="bg-white dark:bg-gray-800 p-6 rounded-lg shadow-md">
          <h2 className="text-xl font-semibold mb-4 dark:text-white">Intelligence Feed</h2>
          <div className="h-[500px]">
            <IntelligenceFeed />
          </div>
        </div>
        
        {/* CISA KEV Section */}
        <div className="bg-white dark:bg-gray-800 p-6 rounded-lg shadow-md">
          <h2 className="text-xl font-semibold mb-4 dark:text-white">CISA Known Exploited Vulnerabilities</h2>
          <div className="h-[500px]">
            <CISAKev />
          </div>
        </div>
      </div>
    </div>
  );
} 