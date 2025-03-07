"use client"

import React, { useState, useEffect } from 'react'
import { fetchCISAKev, CISAKevVulnerability } from '@/lib/api'
import { format, parse, isAfter, isBefore, isEqual } from 'date-fns'
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
  ChevronUp,
  Filter,
  CalendarIcon,
  X
} from 'lucide-react'
import { Badge } from '@/components/ui/badge'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Alert, AlertDescription } from '@/components/ui/alert'

// Types for our filters
interface SearchFilters {
  keyword: string;
  cveId: string;
  vendor: string;
  severity: string;
  product: string;
  startDate: string;
  endDate: string;
}

export default function CISAKevTable() {
  const [vulnerabilities, setVulnerabilities] = useState<CISAKevVulnerability[]>([]);
  const [filteredVulnerabilities, setFilteredVulnerabilities] = useState<CISAKevVulnerability[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  
  // Advanced filters
  const [showAdvancedFilters, setShowAdvancedFilters] = useState(false);
  const [filters, setFilters] = useState<SearchFilters>({
    keyword: '',
    cveId: '',
    vendor: 'all',
    severity: 'all',
    product: '',
    startDate: '',
    endDate: ''
  });
  
  // Filter options
  const [vendors, setVendors] = useState<string[]>([]);
  const [products, setProducts] = useState<string[]>([]);
  const [severityLevels, setSeverityLevels] = useState<string[]>([]);
  
  const [expandedRows, setExpandedRows] = useState<Set<string>>(new Set());

  // Fetch vulnerabilities on component mount
  useEffect(() => {
    fetchData();
  }, []);

  // Filter vulnerabilities when filters change
  useEffect(() => {
    filterVulnerabilities();
  }, [filters, vulnerabilities]);

  // Fetch data from the API
  const fetchData = async () => {
    try {
      setLoading(true);
      const data = await fetchCISAKev();
      setVulnerabilities(data);
      
      // Extract unique filter options
      const uniqueVendors = [...new Set(data.map(vuln => vuln.vendorProject))].filter(Boolean).sort();
      setVendors(uniqueVendors);
      
      const uniqueProducts = [...new Set(data.map(vuln => vuln.product))].filter(Boolean).sort();
      setProducts(uniqueProducts);
      
      const uniqueSeverities = [...new Set(data.map(vuln => vuln.severityLevel))].filter(Boolean).sort();
      setSeverityLevels(uniqueSeverities);
      
      setError(null);
    } catch (err) {
      setError('Failed to fetch CISA KEV data. Please try again later.');
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  // Reset all filters
  const resetFilters = () => {
    setFilters({
      keyword: '',
      cveId: '',
      vendor: 'all',
      severity: 'all',
      product: '',
      startDate: '',
      endDate: ''
    });
  };

  // Handle input change for text and date filters
  const handleFilterChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const { name, value } = e.target;
    setFilters(prev => ({ ...prev, [name]: value }));
  };

  // Handle select filters change
  const handleSelectChange = (name: string, value: string) => {
    setFilters(prev => ({ ...prev, [name]: value }));
  };

  // Filter vulnerabilities based on all criteria
  const filterVulnerabilities = () => {
    let filtered = [...vulnerabilities];
    
    // Keyword search (general)
    if (filters.keyword.trim() !== '') {
      const search = filters.keyword.toLowerCase();
      filtered = filtered.filter(vuln => 
        vuln.cveID.toLowerCase().includes(search) || 
        vuln.vulnerabilityName.toLowerCase().includes(search) ||
        (vuln.shortDescription && vuln.shortDescription.toLowerCase().includes(search)) ||
        vuln.vendorProject.toLowerCase().includes(search) ||
        vuln.product.toLowerCase().includes(search)
      );
    }
    
    // CVE ID specific search
    if (filters.cveId.trim() !== '') {
      const cveSearch = filters.cveId.toLowerCase();
      filtered = filtered.filter(vuln => 
        vuln.cveID.toLowerCase().includes(cveSearch)
      );
    }
    
    // Vendor filter
    if (filters.vendor !== 'all') {
      filtered = filtered.filter(vuln => vuln.vendorProject === filters.vendor);
    }
    
    // Severity filter
    if (filters.severity !== 'all') {
      filtered = filtered.filter(vuln => vuln.severityLevel === filters.severity);
    }
    
    // Product filter
    if (filters.product.trim() !== '') {
      const productSearch = filters.product.toLowerCase();
      filtered = filtered.filter(vuln => 
        vuln.product.toLowerCase().includes(productSearch)
      );
    }
    
    // Date range filter
    if (filters.startDate !== '') {
      const startDate = parse(filters.startDate, 'yyyy-MM-dd', new Date());
      filtered = filtered.filter(vuln => {
        const vulnDate = new Date(vuln.dateAdded);
        return isAfter(vulnDate, startDate) || isEqual(vulnDate, startDate);
      });
    }
    
    if (filters.endDate !== '') {
      const endDate = parse(filters.endDate, 'yyyy-MM-dd', new Date());
      filtered = filtered.filter(vuln => {
        const vulnDate = new Date(vuln.dateAdded);
        return isBefore(vulnDate, endDate) || isEqual(vulnDate, endDate);
      });
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

  // Helper to determine if any advanced filters are active
  const hasActiveAdvancedFilters = () => {
    return (
      filters.cveId.trim() !== '' ||
      filters.vendor !== 'all' ||
      filters.severity !== 'all' ||
      filters.product.trim() !== '' ||
      filters.startDate !== '' ||
      filters.endDate !== ''
    );
  };

  return (
    <Card className="w-full">
      <CardHeader className="pb-2">
        <CardTitle className="text-xl font-semibold">CISA Known Exploited Vulnerabilities</CardTitle>
        
        {/* Basic search bar */}
        <div className="flex flex-col sm:flex-row justify-between gap-4 mt-4">
          <div className="flex items-center gap-2 w-full sm:w-auto">
            <Search className="w-4 h-4 text-gray-500" />
            <Input
              placeholder="Search any field..."
              name="keyword"
              value={filters.keyword}
              onChange={handleFilterChange}
              className="w-full sm:w-64"
            />
          </div>
          <div className="flex gap-2 items-center">
            <Button 
              variant="outline"
              onClick={() => setShowAdvancedFilters(!showAdvancedFilters)}
              className={showAdvancedFilters ? "bg-gray-100" : ""}
            >
              <Filter className="h-4 w-4 mr-2" />
              {showAdvancedFilters ? "Hide Filters" : "Advanced Filters"}
              {hasActiveAdvancedFilters() && !showAdvancedFilters && (
                <Badge className="ml-2 bg-blue-500 text-white" variant="secondary">
                  {Object.values(filters).filter(v => v !== '' && v !== 'all').length}
                </Badge>
              )}
            </Button>
            <Button 
              variant="outline" 
              size="icon" 
              onClick={fetchData} 
            >
              <RefreshCw className="h-4 w-4" />
            </Button>
          </div>
        </div>
        
        {/* Advanced filters */}
        {showAdvancedFilters && (
          <div className="mt-4 p-4 border rounded-md bg-gray-50">
            <div className="flex justify-between items-center mb-3">
              <h3 className="font-medium">Advanced Filters</h3>
              <Button 
                variant="ghost" 
                size="sm" 
                onClick={resetFilters}
                className="h-8 text-xs"
              >
                Reset All
              </Button>
            </div>
            
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
              {/* CVE ID filter */}
              <div>
                <label className="block text-sm font-medium mb-1">CVE ID</label>
                <Input
                  name="cveId"
                  placeholder="e.g. CVE-2023-..."
                  value={filters.cveId}
                  onChange={handleFilterChange}
                  className="w-full"
                />
              </div>
              
              {/* Vendor filter */}
              <div>
                <label className="block text-sm font-medium mb-1">Vendor</label>
                <Select
                  value={filters.vendor}
                  onValueChange={(value) => handleSelectChange('vendor', value)}
                >
                  <SelectTrigger className="w-full">
                    <SelectValue placeholder="All Vendors" />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="all">All Vendors</SelectItem>
                    {vendors.map(vendor => (
                      <SelectItem key={vendor} value={vendor}>{vendor}</SelectItem>
                    ))}
                  </SelectContent>
                </Select>
              </div>
              
              {/* Severity filter */}
              <div>
                <label className="block text-sm font-medium mb-1">Severity</label>
                <Select
                  value={filters.severity}
                  onValueChange={(value) => handleSelectChange('severity', value)}
                >
                  <SelectTrigger className="w-full">
                    <SelectValue placeholder="All Severity Levels" />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="all">All Severity Levels</SelectItem>
                    {severityLevels.map(level => (
                      <SelectItem key={level} value={level}>{level}</SelectItem>
                    ))}
                  </SelectContent>
                </Select>
              </div>
              
              {/* Product filter */}
              <div>
                <label className="block text-sm font-medium mb-1">Product</label>
                <Input
                  name="product"
                  placeholder="Search product..."
                  value={filters.product}
                  onChange={handleFilterChange}
                  className="w-full"
                />
              </div>
              
              {/* Date range filters */}
              <div>
                <label className="block text-sm font-medium mb-1">Date Added (Start)</label>
                <div className="relative">
                  <Input
                    name="startDate"
                    type="date"
                    value={filters.startDate}
                    onChange={handleFilterChange}
                    className="w-full"
                  />
                  <CalendarIcon className="absolute top-2.5 right-3 h-4 w-4 text-gray-400" />
                </div>
              </div>
              
              <div>
                <label className="block text-sm font-medium mb-1">Date Added (End)</label>
                <div className="relative">
                  <Input
                    name="endDate"
                    type="date"
                    value={filters.endDate}
                    onChange={handleFilterChange}
                    className="w-full"
                  />
                  <CalendarIcon className="absolute top-2.5 right-3 h-4 w-4 text-gray-400" />
                </div>
              </div>
            </div>
            
            {/* Active filters display */}
            {hasActiveAdvancedFilters() && (
              <div className="mt-4 flex flex-wrap gap-1.5 items-center">
                <span className="text-sm font-medium text-muted-foreground">Active filters:</span>
                
                {filters.cveId && (
                  <Badge variant="secondary" className="flex items-center gap-1">
                    CVE: {filters.cveId}
                    <X 
                      className="h-3 w-3 cursor-pointer" 
                      onClick={() => setFilters(prev => ({ ...prev, cveId: '' }))}
                    />
                  </Badge>
                )}
                
                {filters.vendor !== 'all' && (
                  <Badge variant="secondary" className="flex items-center gap-1">
                    Vendor: {filters.vendor}
                    <X 
                      className="h-3 w-3 cursor-pointer" 
                      onClick={() => setFilters(prev => ({ ...prev, vendor: 'all' }))}
                    />
                  </Badge>
                )}
                
                {filters.severity !== 'all' && (
                  <Badge variant="secondary" className="flex items-center gap-1">
                    Severity: {filters.severity}
                    <X 
                      className="h-3 w-3 cursor-pointer" 
                      onClick={() => setFilters(prev => ({ ...prev, severity: 'all' }))}
                    />
                  </Badge>
                )}
                
                {filters.product && (
                  <Badge variant="secondary" className="flex items-center gap-1">
                    Product: {filters.product}
                    <X 
                      className="h-3 w-3 cursor-pointer" 
                      onClick={() => setFilters(prev => ({ ...prev, product: '' }))}
                    />
                  </Badge>
                )}
                
                {filters.startDate && (
                  <Badge variant="secondary" className="flex items-center gap-1">
                    From: {filters.startDate}
                    <X 
                      className="h-3 w-3 cursor-pointer" 
                      onClick={() => setFilters(prev => ({ ...prev, startDate: '' }))}
                    />
                  </Badge>
                )}
                
                {filters.endDate && (
                  <Badge variant="secondary" className="flex items-center gap-1">
                    To: {filters.endDate}
                    <X 
                      className="h-3 w-3 cursor-pointer" 
                      onClick={() => setFilters(prev => ({ ...prev, endDate: '' }))}
                    />
                  </Badge>
                )}
              </div>
            )}
          </div>
        )}
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