"use client"

import React, { useState, useEffect, useCallback } from 'react'
import { fetchCrowdStrikeTailoredIntel, isErrorResponse, ApiErrorResponse, clearCache } from '@/lib/api'
import { format } from 'date-fns'
import {
  Table,
  TableBody,
  TableCaption,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "@/components/ui/table"
import { Input } from '@/components/ui/input'
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select'
import { Button } from '@/components/ui/button'
import { 
  RefreshCw,
  Search, 
  AlertCircle,
  ChevronDown,
  ChevronUp,
  ExternalLink,
  AlertTriangle,
  Wifi
} from 'lucide-react'
import { Badge } from '@/components/ui/badge'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Alert, AlertDescription, AlertTitle } from '@/components/ui/alert'

// Create a simple logger for debugging
const logger = {
  error: (message: string, error?: any) => {
    console.error(`[CrowdStrikeTailoredIntelTable] ${message}`, error || '');
  },
  info: (message: string) => {
    console.info(`[CrowdStrikeTailoredIntelTable] ${message}`);
  }
};

export interface CrowdStrikeTailoredIntel {
  id: string;
  name: string;
  summary: string | null;
  publish_date: string;
  last_updated: string;
  url: string | null;
  threat_groups: string[];
  targeted_sectors: string[];
  // New fields
  source?: string;
  hit_type?: string;
  matched_rule_names?: string[];
  details?: string;
  first_seen?: string;
  // Frontend-only fields
  title?: string;
  report_type?: string;
  target_sectors?: string[];
  target_countries?: string[];
  malware_families?: string[];
  tags?: string[];
  published_date?: string;
  confidence_level?: string;
  severity_level?: string;
  report_url?: string | null;
}

export default function CrowdStrikeTailoredIntelTable() {
  const [intelReports, setIntelReports] = useState<CrowdStrikeTailoredIntel[]>([]);
  const [filteredReports, setFilteredReports] = useState<CrowdStrikeTailoredIntel[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [errorType, setErrorType] = useState<'network' | 'server' | 'data' | null>(null);
  const [searchTerm, setSearchTerm] = useState('');
  const [selectedReportType, setSelectedReportType] = useState('all');
  const [selectedSeverity, setSelectedSeverity] = useState('all');
  const [reportTypes, setReportTypes] = useState<string[]>([]);
  const [severityLevels, setSeverityLevels] = useState<string[]>([]);
  const [expandedRows, setExpandedRows] = useState<Set<string>>(new Set());
  const [isRefreshing, setIsRefreshing] = useState(false);
  const [dataFetched, setDataFetched] = useState(false);
  const [retrying, setRetrying] = useState(false);

  // Fetch data on component mount (only on client-side)
  useEffect(() => {
    // Only run data fetching on the client to avoid hydration issues
    if (typeof window !== 'undefined' && !dataFetched) {
      fetchData(false);
      setDataFetched(true);
      
      // Set up periodic refresh (every 15 minutes)
      const intervalId = setInterval(() => {
        fetchData(false);
      }, 15 * 60 * 1000); // 15 minutes in milliseconds
      
      // Clean up interval on component unmount
      return () => clearInterval(intervalId);
    }
  }, [dataFetched]);

  // Filter reports when search term or selected filters change
  useEffect(() => {
    if (intelReports && intelReports.length > 0) {
      filterReports();
    }
  }, [searchTerm, selectedReportType, selectedSeverity, intelReports]);

  // Fetch data from the API
  const fetchData = async (forceRefresh: boolean = false) => {
    try {
      setLoading(true);
      if (forceRefresh) {
        setIsRefreshing(true);
        
        // Call the refresh endpoint directly
        try {
          const backendUrl = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000/api';
          const refreshResponse = await fetch(`${backendUrl}/refresh-tailored-intel/`);
          
          if (!refreshResponse.ok) {
            logger.error('Error refreshing tailored intelligence data');
          } else {
            logger.info('Successfully refreshed tailored intelligence data');
          }
        } catch (refreshError) {
          logger.error('Failed to call refresh endpoint', refreshError);
        }
      }
      
      setError(null);
      setErrorType(null);
      setRetrying(false);
      
      const response = await fetchCrowdStrikeTailoredIntel(forceRefresh);
      
      // Check if the response is an error
      if (isErrorResponse(response)) {
        setError(response.message || 'Failed to fetch CrowdStrike tailored intelligence');
        
        // Set error type based on status code
        if (response.status >= 500) {
          setErrorType('server');
        } else if (response.status === 408 || response.status === 503) {
          setErrorType('network');
        } else {
          setErrorType('data');
        }
        
        setIntelReports([]);
      } else {
        // If we reach here, the response is a successful array of data
        // Map the API response to the expected format
        const formattedData = response.map((item: CrowdStrikeTailoredIntel) => ({
          ...item,
          title: item.name,
          report_type: 'Intelligence Report', 
          // Extract threat actor information from summary if available
          report_url: item.url,
          // Extract target countries from summary if available
          target_countries: item.targeted_sectors.map((sector: string) => 
            sector.includes("Geography:") ? sector.replace("Geography:", "").trim() : ""
          ).filter(Boolean),
          // Default values for filtering
          confidence_level: 'High',
          severity_level: 'Medium', 
        }));
        
        // Extract unique report types and severity levels for filters
        const reportTypeSet = [...new Set(formattedData.map(item => item.report_type || '').filter(Boolean))];
        const severitySet = [...new Set(formattedData.map(item => item.severity_level || '').filter(Boolean))];
        
        setReportTypes(reportTypeSet);
        setSeverityLevels(severitySet);
        setIntelReports(formattedData);
        setError(null);
        setErrorType(null);
      }
    } catch (err) {
      console.error('Error fetching intel reports:', err);
      setError('Failed to fetch CrowdStrike Tailored Intel. Please try again later.');
      setErrorType('network');
      setIntelReports([]);
    } finally {
      setLoading(false);
      setIsRefreshing(false);
    }
  };

  // Handle retry button click
  const handleRetry = useCallback(() => {
    setRetrying(true);
    fetchData(true).finally(() => {
      setRetrying(false);
    });
  }, []);

  // Filter reports based on search term and selected filters
  const filterReports = () => {
    if (!Array.isArray(intelReports)) {
      setFilteredReports([]);
      return;
    }
    
    let filtered = [...intelReports];
    
    // Filter by report type
    if (selectedReportType !== 'all') {
      filtered = filtered.filter(report => report.report_type === selectedReportType);
    }
    
    // Filter by severity
    if (selectedSeverity !== 'all') {
      filtered = filtered.filter(report => report.severity_level === selectedSeverity);
    }
    
    // Filter by search term
    if (searchTerm.trim() !== '') {
      const search = searchTerm.toLowerCase();
      filtered = filtered.filter(report => 
        (report.name?.toLowerCase().includes(search)) || 
        (report.summary?.toLowerCase().includes(search)) ||
        (report.threat_groups?.some(group => group.toLowerCase().includes(search)))
      );
    }
    
    setFilteredReports(filtered);
  };

  // Format date for display
  const formatDate = (dateString: string | null) => {
    if (!dateString) return 'N/A';
    try {
      // Use a fixed timestamp for server-side rendering to avoid hydration errors
      if (typeof window === 'undefined') {
        return 'Loading date...';
      }
      return format(new Date(dateString), 'PPP');
    } catch (error) {
      return 'Invalid date';
    }
  };

  // Toggle row expansion
  const toggleRowExpansion = (reportId: string) => {
    const newExpandedRows = new Set(expandedRows);
    if (newExpandedRows.has(reportId)) {
      newExpandedRows.delete(reportId);
    } else {
      newExpandedRows.add(reportId);
    }
    setExpandedRows(newExpandedRows);
  };

  // Get severity color
  const getSeverityColor = (severity: string = 'Medium') => {
    const colors: Record<string, string> = {
      'Critical': 'bg-red-50 text-red-600 border-red-200',
      'High': 'bg-orange-50 text-orange-600 border-orange-200',
      'Medium': 'bg-yellow-50 text-yellow-600 border-yellow-200',
      'Low': 'bg-blue-50 text-blue-600 border-blue-200',
      'Informational': 'bg-gray-50 text-gray-600 border-gray-200',
    };
    
    return colors[severity] || colors['Medium'];
  };

  // Render different error alerts based on error type
  const renderErrorAlert = () => {
    if (!error) return null;
    
    switch (errorType) {
      case 'network':
        return (
          <Alert variant="destructive" className="mb-4">
            <Wifi className="h-4 w-4" />
            <AlertTitle>Connection Error</AlertTitle>
            <AlertDescription>
              {error}
              <div className="mt-2">
                <Button 
                  variant="outline" 
                  size="sm" 
                  onClick={() => handleRetry()} 
                  disabled={retrying}
                >
                  {retrying ? <RefreshCw className="h-4 w-4 mr-2 animate-spin" /> : <RefreshCw className="h-4 w-4 mr-2" />}
                  Retry Connection
                </Button>
              </div>
            </AlertDescription>
          </Alert>
        );
      case 'server':
        return (
          <Alert variant="destructive" className="mb-4">
            <AlertTriangle className="h-4 w-4" />
            <AlertTitle>Server Error</AlertTitle>
            <AlertDescription>
              {error}
              <div className="mt-2">
                <Button 
                  variant="outline" 
                  size="sm" 
                  onClick={() => handleRetry()} 
                  disabled={retrying}
                >
                  {retrying ? <RefreshCw className="h-4 w-4 mr-2 animate-spin" /> : <RefreshCw className="h-4 w-4 mr-2" />}
                  Retry Request
                </Button>
              </div>
            </AlertDescription>
          </Alert>
        );
      default:
        return (
          <Alert variant="destructive" className="mb-4">
            <AlertCircle className="h-4 w-4" />
            <AlertDescription>{error}</AlertDescription>
          </Alert>
        );
    }
  };

  return (
    <Card className="w-full">
      <CardHeader className="pb-2">
        <CardTitle className="text-xl font-semibold">CrowdStrike Tailored Intelligence</CardTitle>
        <div className="flex flex-col sm:flex-row justify-between gap-4 mt-4">
          <div className="flex items-center gap-2 w-full sm:w-auto">
            <Search className="w-4 h-4 text-gray-500" />
            <Input
              placeholder="Search intelligence reports..."
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
              className="w-full sm:w-64"
            />
          </div>
          <div className="flex flex-wrap gap-2 items-center w-full sm:w-auto">
            <Select
              value={selectedReportType}
              onValueChange={setSelectedReportType}
            >
              <SelectTrigger className="w-full sm:w-40">
                <SelectValue placeholder="All Report Types" />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="all">All Report Types</SelectItem>
                {reportTypes.map(type => (
                  <SelectItem key={type} value={type}>{type}</SelectItem>
                ))}
              </SelectContent>
            </Select>
            
            <Select
              value={selectedSeverity}
              onValueChange={setSelectedSeverity}
            >
              <SelectTrigger className="w-full sm:w-40">
                <SelectValue placeholder="All Severity Levels" />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="all">All Severity Levels</SelectItem>
                {severityLevels.map(level => (
                  <SelectItem key={level} value={level}>{level}</SelectItem>
                ))}
              </SelectContent>
            </Select>
            
            <Button 
              variant="outline" 
              size="icon" 
              onClick={() => fetchData(true)} 
              disabled={isRefreshing || loading}
            >
              <RefreshCw className={`h-4 w-4 ${isRefreshing ? 'animate-spin' : ''}`} />
            </Button>
          </div>
        </div>
      </CardHeader>
      <CardContent>
        {renderErrorAlert()}
        
        {loading ? (
          <div className="flex justify-center items-center py-8">
            <RefreshCw className="h-6 w-6 animate-spin text-gray-400" />
          </div>
        ) : (
          <div className="rounded-md border">
            <Table>
              <TableCaption>
                {filteredReports.length > 0 
                  ? `Showing ${filteredReports.length} of ${intelReports.length} intelligence reports`
                  : 'No matching intelligence reports found'
                }
              </TableCaption>
              <TableHeader>
                <TableRow>
                  <TableHead className="w-[200px]">Name</TableHead>
                  <TableHead>Source</TableHead>
                  <TableHead>Hit Type</TableHead>
                  <TableHead>First Seen</TableHead>
                  <TableHead className="text-right">Actions</TableHead>
                </TableRow>
              </TableHeader>
              <TableBody>
                {filteredReports.length > 0 ? (
                  filteredReports.map((report) => (
                    <React.Fragment key={report.id}>
                      <TableRow>
                        <TableCell className="font-medium">
                          {report.name}
                        </TableCell>
                        <TableCell>
                          {report.source || 'N/A'}
                        </TableCell>
                        <TableCell>
                          {report.hit_type || 'N/A'}
                        </TableCell>
                        <TableCell>
                          {formatDate(report.first_seen || null)}
                        </TableCell>
                        <TableCell className="text-right">
                          <Button
                            variant="ghost"
                            size="sm"
                            onClick={() => toggleRowExpansion(report.id)}
                          >
                            {expandedRows.has(report.id) ? (
                              <ChevronUp className="h-4 w-4 mr-1" />
                            ) : (
                              <ChevronDown className="h-4 w-4 mr-1" />
                            )}
                            {expandedRows.has(report.id) ? 'Hide Details' : 'Show Details'}
                          </Button>
                        </TableCell>
                      </TableRow>
                      {expandedRows.has(report.id) && (
                        <TableRow>
                          <TableCell colSpan={5} className="p-4 bg-gray-50">
                            <div className="space-y-4">
                              <div>
                                <h4 className="text-sm font-semibold mb-1">Summary</h4>
                                <p className="text-sm text-gray-700">{report.summary || 'No summary available'}</p>
                              </div>
                              
                              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                                <div>
                                  <h4 className="text-sm font-semibold mb-1">Threat Groups</h4>
                                  <div className="flex flex-wrap gap-1">
                                    {report.threat_groups && report.threat_groups.length > 0 ? (
                                      report.threat_groups.map((group, index) => (
                                        <Badge key={index} variant="outline" className="bg-red-50 text-red-700 border-red-200">
                                          {group}
                                        </Badge>
                                      ))
                                    ) : (
                                      <span className="text-gray-500 text-sm">None identified</span>
                                    )}
                                  </div>
                                </div>
                                
                                <div>
                                  <h4 className="text-sm font-semibold mb-1">Malware Families</h4>
                                  <div className="flex flex-wrap gap-1">
                                    {report.malware_families && report.malware_families.length > 0 ? (
                                      report.malware_families.map((malware, index) => (
                                        <Badge key={index} variant="outline" className="bg-blue-50 text-blue-700 border-blue-200">
                                          {malware}
                                        </Badge>
                                      ))
                                    ) : (
                                      <span className="text-gray-500 text-sm">None identified</span>
                                    )}
                                  </div>
                                </div>
                              </div>
                              
                              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                                <div>
                                  <h4 className="text-sm font-semibold mb-1">Target Sectors</h4>
                                  <div className="flex flex-wrap gap-1">
                                    {report.target_sectors && report.target_sectors.length > 0 ? (
                                      report.target_sectors.map((sector, index) => (
                                        <Badge key={index} variant="outline" className="bg-purple-50 text-purple-700 border-purple-200">
                                          {sector}
                                        </Badge>
                                      ))
                                    ) : (
                                      <span className="text-gray-500 text-sm">None identified</span>
                                    )}
                                  </div>
                                </div>
                                
                                <div>
                                  <h4 className="text-sm font-semibold mb-1">Target Countries</h4>
                                  <div className="flex flex-wrap gap-1">
                                    {report.target_countries && report.target_countries.length > 0 ? (
                                      report.target_countries.map((country, index) => (
                                        <Badge key={index} variant="outline" className="bg-green-50 text-green-700 border-green-200">
                                          {country}
                                        </Badge>
                                      ))
                                    ) : (
                                      <span className="text-gray-500 text-sm">None identified</span>
                                    )}
                                  </div>
                                </div>
                              </div>
                              
                              <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                                <div>
                                  <h4 className="text-sm font-semibold mb-1">Published Date</h4>
                                  <p className="text-sm">{formatDate(report.published_date || null)}</p>
                                </div>
                                <div>
                                  <h4 className="text-sm font-semibold mb-1">Last Updated</h4>
                                  <p className="text-sm">{formatDate(report.last_updated)}</p>
                                </div>
                                <div>
                                  <h4 className="text-sm font-semibold mb-1">Confidence Level</h4>
                                  <p className="text-sm">{report.confidence_level}</p>
                                </div>
                              </div>
                              
                              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                                <div>
                                  <h4 className="text-sm font-semibold mb-1">Matched Rules</h4>
                                  <div className="flex flex-wrap gap-1">
                                    {report.matched_rule_names && report.matched_rule_names.length > 0 ? (
                                      report.matched_rule_names.map((rule, index) => (
                                        <Badge key={index} variant="outline" className="bg-yellow-50 text-yellow-700 border-yellow-200">
                                          {rule}
                                        </Badge>
                                      ))
                                    ) : (
                                      <span className="text-gray-500 text-sm">None identified</span>
                                    )}
                                  </div>
                                </div>
                                
                                <div>
                                  <h4 className="text-sm font-semibold mb-1">Details</h4>
                                  <p className="text-sm">{report.details || 'No details available'}</p>
                                </div>
                              </div>
                              
                              {report.report_url && (
                                <div>
                                  <a 
                                    href={report.report_url} 
                                    target="_blank" 
                                    rel="noopener noreferrer"
                                    className="inline-flex items-center text-blue-600 hover:text-blue-800 text-sm"
                                  >
                                    <Button size="sm" variant="outline">
                                      <ExternalLink className="h-4 w-4 mr-1" />
                                      View Full Report
                                    </Button>
                                  </a>
                                </div>
                              )}
                            </div>
                          </TableCell>
                        </TableRow>
                      )}
                    </React.Fragment>
                  ))
                ) : (
                  <TableRow>
                    <TableCell colSpan={5} className="h-24 text-center">
                      No results found.
                    </TableCell>
                  </TableRow>
                )}
              </TableBody>
            </Table>
          </div>
        )}
      </CardContent>
    </Card>
  )
} 