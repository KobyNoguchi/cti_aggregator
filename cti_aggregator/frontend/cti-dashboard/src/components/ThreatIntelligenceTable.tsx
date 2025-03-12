"use client"

import React, { useState, useEffect, useCallback } from 'react'
import { fetchIntelligenceArticles, refreshIntelligence, IntelligenceArticle, isErrorResponse, ApiErrorResponse } from '@/lib/api'
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
  ExternalLink, 
  Search, 
  AlertCircle,
  AlertTriangle,
  Wifi
} from 'lucide-react'
import { Badge } from '@/components/ui/badge'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Alert, AlertDescription, AlertTitle } from '@/components/ui/alert'

export default function ThreatIntelligenceTable() {
  const [articles, setArticles] = useState<IntelligenceArticle[]>([]);
  const [filteredArticles, setFilteredArticles] = useState<IntelligenceArticle[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [errorType, setErrorType] = useState<'network' | 'server' | 'data' | null>(null);
  const [refreshing, setRefreshing] = useState(false);
  const [searchTerm, setSearchTerm] = useState('');
  const [selectedSource, setSelectedSource] = useState('all');
  const [sources, setSources] = useState<string[]>([]);
  const [dataFetched, setDataFetched] = useState(false);
  const [retrying, setRetrying] = useState(false);

  // Fetch articles on component mount (only on client-side)
  useEffect(() => {
    // Only run data fetching on the client to avoid hydration issues
    if (typeof window !== 'undefined' && !dataFetched) {
      fetchData();
      setDataFetched(true);
    }
  }, [dataFetched]);

  // Filter articles when search term or selected source changes
  useEffect(() => {
    if (articles && articles.length > 0) {
      filterArticles();
    }
  }, [searchTerm, selectedSource, articles]);

  // Fetch data from the API
  const fetchData = async (skipCache: boolean = false) => {
    try {
      setLoading(true);
      setError(null);
      setErrorType(null);
      setRetrying(false);
      
      const response = await fetchIntelligenceArticles(skipCache);
      
      // Check if the response is an error
      if (isErrorResponse(response)) {
        setError(response.message || 'Failed to fetch intelligence articles');
        
        // Set error type based on status code
        if (response.status >= 500) {
          setErrorType('server');
        } else if (response.status === 408 || response.status === 503) {
          setErrorType('network');
        } else {
          setErrorType('data');
        }
        
        setArticles([]);
      } else {
        // We know it's an array of IntelligenceArticle now
        setArticles(response);
        
        // Extract unique sources for filter dropdown
        const uniqueSources = [...new Set(response.map((article: IntelligenceArticle) => article.source))];
        setSources(uniqueSources);
        
        setError(null);
        setErrorType(null);
      }
    } catch (err) {
      setError('Failed to fetch intelligence articles. Please try again later.');
      setErrorType('network');
      console.error(err);
      setArticles([]);
    } finally {
      setLoading(false);
    }
  };

  // Handle retry button click
  const handleRetry = useCallback(async () => {
    setRetrying(true);
    await fetchData(true); // Skip cache on retry
  }, []);

  // Handle refresh button click
  const handleRefresh = async () => {
    try {
      setRefreshing(true);
      await refreshIntelligence();
      await fetchData(true); // Skip cache on refresh
    } catch (err) {
      setError('Failed to refresh intelligence data. Please try again later.');
      setErrorType('server');
      console.error(err);
    } finally {
      setRefreshing(false);
    }
  };

  // Filter articles based on search term and selected source
  const filterArticles = () => {
    if (!Array.isArray(articles)) {
      setFilteredArticles([]);
      return;
    }
    
    let filtered = [...articles];
    
    if (selectedSource !== 'all') {
      filtered = filtered.filter(article => article.source === selectedSource);
    }
    
    if (searchTerm.trim() !== '') {
      const search = searchTerm.toLowerCase();
      filtered = filtered.filter(article => 
        article.title.toLowerCase().includes(search) || 
        (article.summary && article.summary.toLowerCase().includes(search))
      );
    }
    
    setFilteredArticles(filtered);
  };

  // Format date for display
  const formatDate = (dateString: string) => {
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

  // Get source badge color based on source name
  const getSourceColor = (source: string) => {
    const sourceColors: Record<string, string> = {
      'Microsoft': 'bg-blue-50 text-blue-600 border-blue-200',
      'Unit42': 'bg-orange-50 text-orange-600 border-orange-200',
      'ZScaler': 'bg-purple-50 text-purple-600 border-purple-200',
      'Orange Cyber Defense': 'bg-orange-50 text-orange-600 border-orange-200',
      'Dark Reading': 'bg-slate-50 text-slate-600 border-slate-200',
      'Google TAG': 'bg-red-50 text-red-600 border-red-200',
    };
    
    return sourceColors[source] || 'bg-gray-50 text-gray-600 border-gray-200';
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
                  onClick={handleRetry} 
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
                  onClick={handleRetry} 
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
        <CardTitle className="text-xl font-semibold">Threat Intelligence</CardTitle>
        <div className="flex flex-col sm:flex-row justify-between gap-4 mt-4">
          <div className="flex items-center gap-2 w-full sm:w-auto">
            <Search className="w-4 h-4 text-gray-500" />
            <Input
              placeholder="Search articles..."
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
              className="w-full sm:w-64"
            />
          </div>
          <div className="flex gap-2 items-center w-full sm:w-auto">
            <Select
              value={selectedSource}
              onValueChange={setSelectedSource}
            >
              <SelectTrigger className="w-full sm:w-40">
                <SelectValue placeholder="All Sources" />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="all">All Sources</SelectItem>
                {sources.map(source => (
                  <SelectItem key={source} value={source}>{source}</SelectItem>
                ))}
              </SelectContent>
            </Select>
            <Button 
              variant="outline" 
              size="icon" 
              onClick={handleRefresh} 
              disabled={refreshing}
            >
              <RefreshCw className={`h-4 w-4 ${refreshing ? 'animate-spin' : ''}`} />
            </Button>
          </div>
        </div>
      </CardHeader>
      <CardContent>
        {error && renderErrorAlert()}
        
        {loading ? (
          <div className="flex justify-center items-center py-8">
            <RefreshCw className="h-6 w-6 animate-spin text-gray-400" />
          </div>
        ) : (
          <div className="rounded-md border">
            <Table>
              <TableCaption>
                {filteredArticles && filteredArticles.length > 0 
                  ? `Showing ${filteredArticles.length} of ${articles.length} articles`
                  : 'No matching articles found'
                }
              </TableCaption>
              <TableHeader>
                <TableRow>
                  <TableHead>Title</TableHead>
                  <TableHead>Source</TableHead>
                  <TableHead>Published Date</TableHead>
                  <TableHead>Threat Actor Type</TableHead>
                  <TableHead>Target Industries</TableHead>
                  <TableHead className="text-right">Actions</TableHead>
                </TableRow>
              </TableHeader>
              <TableBody>
                {filteredArticles && filteredArticles.length > 0 ? (
                  filteredArticles.map((article) => (
                    <TableRow key={article.id}>
                      <TableCell className="font-medium">{article.title}</TableCell>
                      <TableCell>
                        <Badge variant="outline" className={getSourceColor(article.source)}>
                          {article.source}
                        </Badge>
                      </TableCell>
                      <TableCell>{formatDate(article.published_date)}</TableCell>
                      <TableCell>{article.threat_actor_type || 'N/A'}</TableCell>
                      <TableCell>{article.target_industries || 'N/A'}</TableCell>
                      <TableCell className="text-right">
                        <Button variant="ghost" size="sm" asChild>
                          <a href={article.url} target="_blank" rel="noopener noreferrer">
                            <ExternalLink className="h-4 w-4" />
                          </a>
                        </Button>
                      </TableCell>
                    </TableRow>
                  ))
                ) : (
                  <TableRow>
                    <TableCell colSpan={4} className="h-24 text-center">
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