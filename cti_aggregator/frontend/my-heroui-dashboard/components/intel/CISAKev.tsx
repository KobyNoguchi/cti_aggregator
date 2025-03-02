"use client";

import React, { useState, useEffect } from 'react';

interface Vulnerability {
  id: string;
  cveID?: string;
  vulnerabilityName?: string;
  dateAdded?: string;
  shortDescription?: string;
  requiredAction?: string;
  dueDate?: string;
  vendorProject?: string;
  product?: string;
  severityLevel?: string;
}

const CISAKev: React.FC = () => {
  const [vulnerabilities, setVulnerabilities] = useState<Vulnerability[]>([]);
  const [loading, setLoading] = useState(true);
  const [searchTerm, setSearchTerm] = useState('');
  const [selectedVendor, setSelectedVendor] = useState('all');
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const fetchVulnerabilities = async () => {
      const endpoint = 'http://localhost:8000/api/cisa/kev/';
      
      try {
        setLoading(true);
        console.log(`Fetching CISA KEV data from: ${endpoint}`);
        const response = await fetch(endpoint);
        
        if (response.ok) {
          const data = await response.json();
          console.log('CISA KEV data fetched successfully:', data);
          setVulnerabilities(data);
        } else {
          throw new Error(`Server returned ${response.status}: ${response.statusText}`);
        }
      } catch (error: any) {
        console.error("Error fetching CISA KEV data:", error);
        setError(`Failed to load CISA KEV data: ${error.message}. Please make sure your Django backend is running and the CISA KEV endpoint is available.`);
      } finally {
        setLoading(false);
      }
    };

    fetchVulnerabilities();
  }, []);

  // Filter vulnerabilities based on search term and selected vendor
  const filteredVulnerabilities = vulnerabilities.filter(vuln => {
    const matchesSearch = 
      vuln.cveID?.toLowerCase().includes(searchTerm.toLowerCase()) ||
      vuln.vulnerabilityName?.toLowerCase().includes(searchTerm.toLowerCase()) ||
      vuln.shortDescription?.toLowerCase().includes(searchTerm.toLowerCase());
    
    const matchesVendor = selectedVendor === 'all' || vuln.vendorProject === selectedVendor;
    
    return matchesSearch && matchesVendor;
  });

  const handleSearchChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    setSearchTerm(e.target.value);
  };

  const handleVendorChange = (e: React.ChangeEvent<HTMLSelectElement>) => {
    setSelectedVendor(e.target.value);
  };

  // Get unique vendors for the filter dropdown
  const vendors = ['all', ...Array.from(new Set(vulnerabilities
    .map(vuln => vuln.vendorProject)
    .filter(Boolean) as string[]))];

  if (loading) return (
    <div className="flex justify-center items-center h-full">
      <div className="h-8 w-8 animate-spin rounded-full border-b-2 border-primary"></div>
    </div>
  );
  
  if (error) return (
    <div className="bg-red-50 dark:bg-red-900/20 p-4 rounded-md border border-red-200 dark:border-red-800">
      <p className="text-red-700 dark:text-red-400">{error}</p>
      <div className="mt-2 text-xs text-gray-600 dark:text-gray-400">
        <p>API endpoint for CISA KEV data:</p>
        <ul className="mt-1 list-disc pl-5">
          <li>/api/cisa/kev/</li>
        </ul>
        <p className="mt-2">Make sure your Django backend server is running and the CISA KEV endpoint is properly configured.</p>
      </div>
    </div>
  );

  return (
    <div className="h-full">
      <div className="flex mb-4 gap-2">
        <div className="relative flex-1">
          <input
            type="text"
            placeholder="Search vulnerabilities..."
            value={searchTerm}
            onChange={handleSearchChange}
            className="w-full px-3 py-2 border border-gray-300 rounded-md pl-10 dark:bg-gray-800 dark:border-gray-700 dark:text-white"
          />
          <div className="absolute left-3 top-2.5 h-5 w-5 text-gray-400">
            <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
            </svg>
          </div>
        </div>
        <select
          value={selectedVendor}
          onChange={handleVendorChange}
          className="px-3 py-2 border border-gray-300 rounded-md w-[150px] dark:bg-gray-800 dark:border-gray-700 dark:text-white"
        >
          {vendors.map(vendor => (
            <option key={vendor} value={vendor}>
              {vendor === 'all' ? 'All Vendors' : vendor}
            </option>
          ))}
        </select>
      </div>

      <div className="overflow-y-auto h-[calc(100%-40px)] pr-2">
        {filteredVulnerabilities.length > 0 ? (
          <div className="space-y-4">
            {filteredVulnerabilities.map((vuln) => (
              <div key={vuln.id} className="border rounded-md p-4 transition-all hover:shadow-md dark:bg-gray-800 dark:border-gray-700">
                <div className="flex justify-between items-center mb-2">
                  <span className="inline-flex items-center rounded-full bg-red-100 px-2.5 py-0.5 text-xs font-medium text-red-800 dark:bg-red-900 dark:text-red-200">
                    {vuln.cveID || 'No CVE'}
                  </span>
                  <span className="text-xs text-gray-500 dark:text-gray-400">
                    {vuln.dateAdded ? new Date(vuln.dateAdded).toLocaleDateString() : 'Unknown date'}
                  </span>
                </div>
                
                <h3 className="text-sm font-semibold mb-2 dark:text-white">
                  {vuln.vulnerabilityName || 'Unnamed Vulnerability'}
                </h3>
                
                {vuln.shortDescription ? (
                  <p className="text-sm text-gray-700 dark:text-gray-300 mb-3">
                    {vuln.shortDescription.length > 150 
                      ? `${vuln.shortDescription.substring(0, 150)}...` 
                      : vuln.shortDescription}
                  </p>
                ) : (
                  <p className="text-sm text-gray-500 dark:text-gray-400 mb-3">No description available</p>
                )}

                <div className="grid grid-cols-2 gap-2 text-xs">
                  <div>
                    <span className="font-medium text-gray-600 dark:text-gray-400">Vendor: </span>
                    <span className="text-gray-800 dark:text-gray-300">{vuln.vendorProject || 'Unknown'}</span>
                  </div>
                  <div>
                    <span className="font-medium text-gray-600 dark:text-gray-400">Product: </span>
                    <span className="text-gray-800 dark:text-gray-300">{vuln.product || 'Unknown'}</span>
                  </div>
                  <div>
                    <span className="font-medium text-gray-600 dark:text-gray-400">Due Date: </span>
                    <span className="text-gray-800 dark:text-gray-300">
                      {vuln.dueDate ? new Date(vuln.dueDate).toLocaleDateString() : 'Not specified'}
                    </span>
                  </div>
                  <div>
                    <span className="font-medium text-gray-600 dark:text-gray-400">Severity: </span>
                    <span className={`font-medium ${
                      vuln.severityLevel?.toLowerCase().includes('critical') ? 'text-red-600 dark:text-red-400' :
                      vuln.severityLevel?.toLowerCase().includes('high') ? 'text-orange-600 dark:text-orange-400' :
                      vuln.severityLevel?.toLowerCase().includes('medium') ? 'text-yellow-600 dark:text-yellow-400' :
                      'text-green-600 dark:text-green-400'
                    }`}>
                      {vuln.severityLevel || 'Unknown'}
                    </span>
                  </div>
                </div>

                {vuln.requiredAction && (
                  <div className="mt-3 pt-3 border-t border-gray-200 dark:border-gray-700">
                    <p className="text-xs text-gray-700 dark:text-gray-300">
                      <span className="font-medium">Required Action: </span>
                      {vuln.requiredAction}
                    </p>
                  </div>
                )}
              </div>
            ))}
          </div>
        ) : (
          <div className="flex justify-center items-center h-full text-gray-500 dark:text-gray-400">
            <p>No vulnerabilities found matching your criteria.</p>
          </div>
        )}
      </div>
    </div>
  );
};

export default CISAKev; 