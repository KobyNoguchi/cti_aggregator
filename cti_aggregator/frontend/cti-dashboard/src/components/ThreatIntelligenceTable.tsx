"use client"

import React, { useState, useEffect } from 'react'
import { fetchIntelligenceArticles, refreshIntelligence, IntelligenceArticle } from '@/lib/api'
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
  AlertCircle 
} from 'lucide-react'
import { Badge } from '@/components/ui/badge'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Alert, AlertDescription } from '@/components/ui/alert'

export default function ThreatIntelligenceTable() {
  const [articles, setArticles] = useState<IntelligenceArticle[]>([]);
  const [filteredArticles, setFilteredArticles] = useState<IntelligenceArticle[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [refreshing, setRefreshing] = useState(false);
  const [searchTerm, setSearchTerm] = useState('');
  const [selectedSource, setSelectedSource] = useState('all');
  const [sources, setSources] = useState<string[]>([]);

  // Fetch articles on component mount
  useEffect(() => {
    fetchData();
  }, []);

  // Filter articles when search term or selected source changes
  useEffect(() => {
    filterArticles();
  }, [searchTerm, selectedSource, articles]);

  // Fetch data from the API
  const fetchData = async () => {
    try {
      setLoading(true);
      const data = await fetchIntelligenceArticles();
      setArticles(data);
      
      // Extract unique sources for filter dropdown
      const uniqueSources = [...new Set(data.map(article => article.source))];
      setSources(uniqueSources);
      
      setError(null);
    } catch (err) {
      setError('Failed to fetch intelligence articles. Please try again later.');
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  // Handle refresh button click
  const handleRefresh = async () => {
    try {
      setRefreshing(true);
      await refreshIntelligence();
      await fetchData();
    } catch (err) {
      setError('Failed to refresh intelligence data. Please try again later.');
      console.error(err);
    } finally {
      setRefreshing(false);
    }
  };

  // Filter articles based on search term and selected source
  const filterArticles = () => {
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
                {filteredArticles.length > 0 
                  ? `Showing ${filteredArticles.length} of ${articles.length} articles`
                  : 'No matching articles found'
                }
              </TableCaption>
              <TableHeader>
                <TableRow>
                  <TableHead className="w-[160px]">Source</TableHead>
                  <TableHead>Title</TableHead>
                  <TableHead>Date</TableHead>
                  <TableHead className="text-right">Actions</TableHead>
                </TableRow>
              </TableHeader>
              <TableBody>
                {filteredArticles.length > 0 ? (
                  filteredArticles.map((article) => (
                    <TableRow key={article.id}>
                      <TableCell>
                        <Badge className={`${getSourceColor(article.source)} px-2 py-1 text-xs font-medium`}>
                          {article.source}
                        </Badge>
                      </TableCell>
                      <TableCell className="font-medium">
                        <div>
                          <div className="font-medium">{article.title}</div>
                          {article.summary && (
                            <div className="text-sm text-gray-500 mt-1 line-clamp-2">
                              {article.summary}
                            </div>
                          )}
                        </div>
                      </TableCell>
                      <TableCell>{formatDate(article.published_date)}</TableCell>
                      <TableCell className="text-right">
                        <a 
                          href={article.url} 
                          target="_blank" 
                          rel="noopener noreferrer"
                          className="inline-flex items-center text-blue-600 hover:text-blue-800"
                        >
                          <Button size="sm" variant="ghost">
                            <ExternalLink className="h-4 w-4 mr-1" />
                            View
                          </Button>
                        </a>
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