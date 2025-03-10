"use client"

import React, { useState, useEffect } from 'react'
import { fetchCrowdStrikeTailoredIntel, CrowdStrikeTailoredIntel } from '@/lib/api'
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
  ExternalLink
} from 'lucide-react'
import { Badge } from '@/components/ui/badge'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Alert, AlertDescription } from '@/components/ui/alert'

export default function CrowdStrikeTailoredIntelTable() {
  const [intelReports, setIntelReports] = useState<CrowdStrikeTailoredIntel[]>([]);
  const [filteredReports, setFilteredReports] = useState<CrowdStrikeTailoredIntel[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [searchTerm, setSearchTerm] = useState('');
  const [selectedReportType, setSelectedReportType] = useState('all');
  const [selectedSeverity, setSelectedSeverity] = useState('all');
  const [reportTypes, setReportTypes] = useState<string[]>([]);
  const [severityLevels, setSeverityLevels] = useState<string[]>([]);
  const [expandedRows, setExpandedRows] = useState<Set<string>>(new Set());

  // Fetch data on component mount
  useEffect(() => {
    fetchData();
    
    // Set up hourly refresh
    const intervalId = setInterval(() => {
      fetchData();
    }, 60 * 60 * 1000); // 1 hour in milliseconds
    
    // Clean up interval on component unmount
    return () => clearInterval(intervalId);
  }, []);

  // Filter reports when search term or selected filters change
  useEffect(() => {
    filterReports();
  }, [searchTerm, selectedReportType, selectedSeverity, intelReports]);

  // Fetch data from the API
  const fetchData = async () => {
    try {
      setLoading(true);
      const data = await fetchCrowdStrikeTailoredIntel();
      
      // Map the API response to the expected format
      const formattedData = data.map(item => ({
        ...item,
        title: item.name,
        report_type: 'Intelligence Report', 
        target_sectors: item.targeted_sectors || [],
        target_countries: [], 
        malware_families: [], 
        tags: [], 
        published_date: item.publish_date,
        confidence_level: 'Medium', 
        severity_level: 'Medium', 
        report_url: item.url
      }));
      
      setIntelReports(formattedData);
      
      // Extract unique report types for filter dropdown
      const uniqueReportTypes = [...new Set(formattedData.map(report => report.report_type || ''))].filter(Boolean).sort();
      setReportTypes(uniqueReportTypes as string[]);
      
      // Extract unique severity levels for filter dropdown
      const uniqueSeverityLevels = [...new Set(formattedData.map(report => report.severity_level || ''))].filter(Boolean).sort();
      setSeverityLevels(uniqueSeverityLevels as string[]);
      
      setError(null);
    } catch (err) {
      setError('Failed to fetch CrowdStrike Tailored Intelligence data. Please check that the API credentials are properly configured in the backend .env file.');
      console.error(err);
      setIntelReports([]);
    } finally {
      setLoading(false);
    }
  };

  // Filter reports based on search term and selected filters
  const filterReports = () => {
    let filtered = [...intelReports];
    
    if (selectedReportType !== 'all') {
      filtered = filtered.filter(report => report.report_type === selectedReportType);
    }
    
    if (selectedSeverity !== 'all') {
      filtered = filtered.filter(report => report.severity_level === selectedSeverity);
    }
    
    if (searchTerm.trim() !== '') {
      const search = searchTerm.toLowerCase();
      filtered = filtered.filter(report => 
        (report.title || '').toLowerCase().includes(search) || 
        (report.summary && report.summary.toLowerCase().includes(search)) ||
        (report.threat_groups && report.threat_groups.some(group => group.toLowerCase().includes(search))) ||
        (report.malware_families && report.malware_families.some(malware => malware.toLowerCase().includes(search))) ||
        (report.target_sectors && report.target_sectors.some(sector => sector.toLowerCase().includes(search))) ||
        (report.target_countries && report.target_countries.some(country => country.toLowerCase().includes(search)))
      );
    }
    
    setFilteredReports(filtered);
  };

  // Format date for display
  const formatDate = (dateString: string | null) => {
    if (!dateString) return 'N/A';
    try {
      return format(new Date(dateString), 'MMM d, yyyy');
    } catch (error) {
      return dateString;
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

  // Get appropriate color for severity badge
  const getSeverityColor = (severity: string = 'Medium') => {
    const severityColors = {
      'Critical': 'bg-red-50 text-red-600 border-red-200',
      'High': 'bg-orange-50 text-orange-600 border-orange-200',
      'Medium': 'bg-yellow-50 text-yellow-600 border-yellow-200',
      'Low': 'bg-green-50 text-green-600 border-green-200',
    };
    
    return severityColors[severity as keyof typeof severityColors] || 'bg-gray-50 text-gray-600 border-gray-200';
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
              onClick={fetchData} 
            >
              <RefreshCw className="h-4 w-4" />
            </Button>
          </div>
        </div>
      </CardHeader>
      <CardContent>
        {error && (
          <Alert variant="destructive" className="mb-4">
            <AlertCircle className="h-4 w-4" />
            <AlertDescription>{error}</AlertDescription>
          </Alert>
        )}
        
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
                  <TableHead className="w-[50px]"></TableHead>
                  <TableHead>Title</TableHead>
                  <TableHead className="hidden md:table-cell">Report Type</TableHead>
                  <TableHead className="hidden md:table-cell">Severity</TableHead>
                  <TableHead className="hidden md:table-cell">Published Date</TableHead>
                </TableRow>
              </TableHeader>
              <TableBody>
                {filteredReports.length > 0 ? (
                  filteredReports.map((report) => (
                    <React.Fragment key={report.id}>
                      <TableRow
                        className="cursor-pointer"
                        onClick={() => toggleRowExpansion(report.id)}
                      >
                        <TableCell>
                          {expandedRows.has(report.id) ? (
                            <ChevronUp className="h-4 w-4" />
                          ) : (
                            <ChevronDown className="h-4 w-4" />
                          )}
                        </TableCell>
                        <TableCell className="font-medium">
                          {report.title}
                        </TableCell>
                        <TableCell className="hidden md:table-cell">
                          {report.report_type}
                        </TableCell>
                        <TableCell className="hidden md:table-cell">
                          <Badge className={`${getSeverityColor(report.severity_level)} px-2 py-1`}>
                            {report.severity_level}
                          </Badge>
                        </TableCell>
                        <TableCell className="hidden md:table-cell">
                          {formatDate(report.published_date || null)}
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