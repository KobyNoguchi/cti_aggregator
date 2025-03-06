"use client"

import React, { useState, useEffect } from 'react'
import { fetchCISAKev, CISAKevVulnerability } from '@/lib/api'
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
  ExternalLink,
  ChevronDown,
  ChevronUp
} from 'lucide-react'
import { Badge } from '@/components/ui/badge'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Alert, AlertDescription } from '@/components/ui/alert'

export default function CISAKevTable() {
  const [vulnerabilities, setVulnerabilities] = useState<CISAKevVulnerability[]>([]);
  const [filteredVulnerabilities, setFilteredVulnerabilities] = useState<CISAKevVulnerability[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [searchTerm, setSearchTerm] = useState('');
  const [selectedVendor, setSelectedVendor] = useState('all');
  const [vendors, setVendors] = useState<string[]>([]);
  const [expandedRows, setExpandedRows] = useState<Set<string>>(new Set());

  // Fetch vulnerabilities on component mount
  useEffect(() => {
    fetchData();
  }, []);

  // Filter vulnerabilities when search term or selected vendor changes
  useEffect(() => {
    filterVulnerabilities();
  }, [searchTerm, selectedVendor, vulnerabilities]);

  // Fetch data from the API
  const fetchData = async () => {
    try {
      setLoading(true);
      const data = await fetchCISAKev();
      setVulnerabilities(data);
      
      // Extract unique vendors for filter dropdown
      const uniqueVendors = [...new Set(data.map(vuln => vuln.vendorProject))].filter(Boolean);
      setVendors(uniqueVendors);
      
      setError(null);
    } catch (err) {
      setError('Failed to fetch CISA KEV data. Please try again later.');
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  // Filter vulnerabilities based on search term and selected vendor
  const filterVulnerabilities = () => {
    let filtered = [...vulnerabilities];
    
    if (selectedVendor !== 'all') {
      filtered = filtered.filter(vuln => vuln.vendorProject === selectedVendor);
    }
    
    if (searchTerm.trim() !== '') {
      const search = searchTerm.toLowerCase();
      filtered = filtered.filter(vuln => 
        vuln.cveID.toLowerCase().includes(search) || 
        vuln.vulnerabilityName.toLowerCase().includes(search) ||
        (vuln.shortDescription && vuln.shortDescription.toLowerCase().includes(search))
      );
    }
    
    setFilteredVulnerabilities(filtered);
  };

  // Format date for display
  const formatDate = (dateString: string | null) => {
    if (!dateString) return 'N/A';
    try {
      return format(new Date(dateString), 'PPP');
    } catch (error) {
      return 'Invalid date';
    }
  };

  // Toggle row expansion
  const toggleRowExpansion = (vulnId: string) => {
    const newExpandedRows = new Set(expandedRows);
    if (newExpandedRows.has(vulnId)) {
      newExpandedRows.delete(vulnId);
    } else {
      newExpandedRows.add(vulnId);
    }
    setExpandedRows(newExpandedRows);
  };

  // Get severity badge color
  const getSeverityColor = (severity: string) => {
    const severityColors: Record<string, string> = {
      'Critical': 'bg-red-50 text-red-600 border-red-200',
      'High': 'bg-orange-50 text-orange-600 border-orange-200',
      'Medium': 'bg-yellow-50 text-yellow-600 border-yellow-200',
      'Low': 'bg-green-50 text-green-600 border-green-200',
    };
    
    return severityColors[severity] || 'bg-gray-50 text-gray-600 border-gray-200';
  };

  // Generate NVD URL for a CVE
  const getNvdUrl = (cveId: string) => {
    return `https://nvd.nist.gov/vuln/detail/${cveId}`;
  };

  return (
    <Card className="w-full">
      <CardHeader className="pb-2">
        <CardTitle className="text-xl font-semibold">CISA Known Exploited Vulnerabilities</CardTitle>
        <div className="flex flex-col sm:flex-row justify-between gap-4 mt-4">
          <div className="flex items-center gap-2 w-full sm:w-auto">
            <Search className="w-4 h-4 text-gray-500" />
            <Input
              placeholder="Search vulnerabilities..."
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
              className="w-full sm:w-64"
            />
          </div>
          <div className="flex gap-2 items-center w-full sm:w-auto">
            <Select
              value={selectedVendor}
              onValueChange={setSelectedVendor}
            >
              <SelectTrigger className="w-full sm:w-40">
                <SelectValue placeholder="All Vendors" />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="all">All Vendors</SelectItem>
                {vendors.map(vendor => (
                  <SelectItem key={vendor} value={vendor}>{vendor}</SelectItem>
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
                {filteredVulnerabilities.length > 0 
                  ? `Showing ${filteredVulnerabilities.length} of ${vulnerabilities.length} vulnerabilities`
                  : 'No matching vulnerabilities found'
                }
              </TableCaption>
              <TableHeader>
                <TableRow>
                  <TableHead className="w-[50px]"></TableHead>
                  <TableHead className="w-[130px]">CVE ID</TableHead>
                  <TableHead>Name</TableHead>
                  <TableHead className="hidden md:table-cell">Vendor</TableHead>
                  <TableHead className="hidden md:table-cell w-[100px]">Severity</TableHead>
                  <TableHead className="hidden md:table-cell">Added Date</TableHead>
                </TableRow>
              </TableHeader>
              <TableBody>
                {filteredVulnerabilities.length > 0 ? (
                  filteredVulnerabilities.map((vuln) => (
                    <React.Fragment key={vuln.id}>
                      <TableRow
                        className="cursor-pointer"
                        onClick={() => toggleRowExpansion(vuln.id)}
                      >
                        <TableCell>
                          {expandedRows.has(vuln.id) ? (
                            <ChevronUp className="h-4 w-4" />
                          ) : (
                            <ChevronDown className="h-4 w-4" />
                          )}
                        </TableCell>
                        <TableCell className="font-mono text-sm">
                          {vuln.cveID}
                        </TableCell>
                        <TableCell className="font-medium">
                          {vuln.vulnerabilityName}
                        </TableCell>
                        <TableCell className="hidden md:table-cell">
                          {vuln.vendorProject}
                        </TableCell>
                        <TableCell className="hidden md:table-cell">
                          <Badge className={`${getSeverityColor(vuln.severityLevel)} px-2 py-1`}>
                            {vuln.severityLevel}
                          </Badge>
                        </TableCell>
                        <TableCell className="hidden md:table-cell">
                          {formatDate(vuln.dateAdded)}
                        </TableCell>
                      </TableRow>
                      {expandedRows.has(vuln.id) && (
                        <TableRow>
                          <TableCell colSpan={6} className="p-4 bg-gray-50">
                            <div className="space-y-4">
                              <div>
                                <h4 className="text-sm font-semibold mb-1">Description</h4>
                                <p className="text-sm text-gray-700">{vuln.shortDescription || 'No description available'}</p>
                              </div>
                              
                              <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                                <div>
                                  <h4 className="text-sm font-semibold mb-1">Vendor</h4>
                                  <p className="text-sm">{vuln.vendorProject}</p>
                                </div>
                                <div>
                                  <h4 className="text-sm font-semibold mb-1">Product</h4>
                                  <p className="text-sm">{vuln.product}</p>
                                </div>
                                <div>
                                  <h4 className="text-sm font-semibold mb-1">Added to KEV</h4>
                                  <p className="text-sm">{formatDate(vuln.dateAdded)}</p>
                                </div>
                              </div>
                              
                              <div>
                                <h4 className="text-sm font-semibold mb-1">Required Action</h4>
                                <p className="text-sm text-gray-700">{vuln.requiredAction}</p>
                              </div>
                              
                              <div>
                                <a 
                                  href={getNvdUrl(vuln.cveID)} 
                                  target="_blank" 
                                  rel="noopener noreferrer"
                                  className="inline-flex items-center text-blue-600 hover:text-blue-800 text-sm"
                                >
                                  <Button size="sm" variant="outline">
                                    <ExternalLink className="h-4 w-4 mr-1" />
                                    View in NVD
                                  </Button>
                                </a>
                              </div>
                            </div>
                          </TableCell>
                        </TableRow>
                      )}
                    </React.Fragment>
                  ))
                ) : (
                  <TableRow>
                    <TableCell colSpan={6} className="h-24 text-center">
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