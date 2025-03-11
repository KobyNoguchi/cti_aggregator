"use client"

import React, { useState, useEffect, useCallback } from 'react'
import { fetchCrowdStrikeActors, CrowdStrikeActor, isErrorResponse, ApiErrorResponse } from '@/lib/api'
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
  Globe,
  AlertTriangle,
  Wifi,
  ExternalLink
} from 'lucide-react'
import { Badge } from '@/components/ui/badge'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Alert, AlertDescription, AlertTitle } from '@/components/ui/alert'

export default function CrowdStrikeActorsTable() {
  const [actors, setActors] = useState<CrowdStrikeActor[]>([]);
  const [filteredActors, setFilteredActors] = useState<CrowdStrikeActor[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [errorType, setErrorType] = useState<'network' | 'server' | 'data' | null>(null);
  const [searchTerm, setSearchTerm] = useState('');
  const [selectedAdversaryType, setSelectedAdversaryType] = useState('all');
  const [selectedOrigin, setSelectedOrigin] = useState('all');
  const [adversaryTypes, setAdversaryTypes] = useState<string[]>([]);
  const [origins, setOrigins] = useState<string[]>([]);
  const [expandedRows, setExpandedRows] = useState<Set<string>>(new Set());
  const [dataFetched, setDataFetched] = useState(false);
  const [retrying, setRetrying] = useState(false);

  // Fetch data on component mount (only on client-side)
  useEffect(() => {
    // Only run data fetching on the client to avoid hydration issues
    if (typeof window !== 'undefined' && !dataFetched) {
      fetchData();
      setDataFetched(true);
      
      // Set up hourly refresh
      const intervalId = setInterval(() => {
        fetchData(false);
      }, 60 * 60 * 1000); // 1 hour in milliseconds
      
      // Clean up interval on component unmount
      return () => clearInterval(intervalId);
    }
  }, [dataFetched]);

  // Filter actors when search term or selected filters change
  useEffect(() => {
    if (actors && actors.length > 0) {
      filterActors();
    }
  }, [searchTerm, selectedAdversaryType, selectedOrigin, actors]);

  // Fetch data from the API
  const fetchData = async (skipCache: boolean = false) => {
    try {
      setLoading(true);
      setError(null);
      setErrorType(null);
      setRetrying(false);
      
      const response = await fetchCrowdStrikeActors(skipCache);
      
      // Check if the response is an error
      if (isErrorResponse(response)) {
        setError(response.message || 'Failed to fetch CrowdStrike actor data');
        
        // Set error type based on status code
        if (response.status >= 500) {
          setErrorType('server');
        } else if (response.status === 408 || response.status === 503) {
          setErrorType('network');
        } else {
          setErrorType('data');
        }
        
        setActors([]);
      } else {
        // We know it's an array of CrowdStrikeActor now
        setActors(response);
        
        // Extract unique adversary types for filter dropdown
        const uniqueAdversaryTypes = [...new Set(response.map(actor => actor.adversary_type))].filter(Boolean).sort();
        setAdversaryTypes(uniqueAdversaryTypes as string[]);
        
        // Extract unique origins for filter dropdown
        const allOrigins = response.flatMap(actor => actor.origins || []);
        const uniqueOrigins = [...new Set(allOrigins)].filter(Boolean).sort();
        setOrigins(uniqueOrigins as string[]);
        
        setError(null);
        setErrorType(null);
      }
    } catch (err) {
      setError('Failed to fetch CrowdStrike actor data. Please try again later.');
      setErrorType('network');
      console.error(err);
      setActors([]);
    } finally {
      setLoading(false);
    }
  };

  // Handle retry button click
  const handleRetry = useCallback(() => {
    setRetrying(true);
    fetchData(true).finally(() => {
      setRetrying(false);
    });
  }, []);

  // Filter actors based on search term and selected filters
  const filterActors = () => {
    if (!Array.isArray(actors)) {
      setFilteredActors([]);
      return;
    }
    
    let filtered = [...actors];
    
    if (selectedAdversaryType !== 'all') {
      filtered = filtered.filter(actor => actor.adversary_type === selectedAdversaryType);
    }
    
    if (selectedOrigin !== 'all') {
      filtered = filtered.filter(actor => actor.origins?.includes(selectedOrigin));
    }
    
    if (searchTerm.trim() !== '') {
      const search = searchTerm.toLowerCase();
      filtered = filtered.filter(actor => 
        actor.name.toLowerCase().includes(search) || 
        (actor.description && actor.description.toLowerCase().includes(search)) ||
        (actor.capabilities && actor.capabilities.some(cap => cap.toLowerCase().includes(search))) ||
        (actor.objectives && actor.objectives.some(obj => obj.toLowerCase().includes(search)))
      );
    }
    
    setFilteredActors(filtered);
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
  const toggleRowExpansion = (actorId: string) => {
    const newExpandedRows = new Set(expandedRows);
    if (newExpandedRows.has(actorId)) {
      newExpandedRows.delete(actorId);
    } else {
      newExpandedRows.add(actorId);
    }
    setExpandedRows(newExpandedRows);
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
        <CardTitle className="text-xl font-semibold">CrowdStrike Threat Actors</CardTitle>
        <div className="flex flex-col sm:flex-row justify-between gap-4 mt-4">
          <div className="flex items-center gap-2 w-full sm:w-auto">
            <Search className="w-4 h-4 text-gray-500" />
            <Input
              placeholder="Search actors..."
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
              className="w-full sm:w-64"
            />
          </div>
          <div className="flex flex-wrap gap-2 items-center w-full sm:w-auto">
            <Select
              value={selectedAdversaryType}
              onValueChange={setSelectedAdversaryType}
            >
              <SelectTrigger className="w-full sm:w-40">
                <SelectValue placeholder="Adversary Type" />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="all">All Types</SelectItem>
                {adversaryTypes.map(type => (
                  <SelectItem key={type} value={type}>{type}</SelectItem>
                ))}
              </SelectContent>
            </Select>
            
            <Select
              value={selectedOrigin}
              onValueChange={setSelectedOrigin}
            >
              <SelectTrigger className="w-full sm:w-40">
                <SelectValue placeholder="Origin" />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="all">All Origins</SelectItem>
                {origins.map(origin => (
                  <SelectItem key={origin} value={origin}>{origin}</SelectItem>
                ))}
              </SelectContent>
            </Select>
            
            <Button 
              variant="outline" 
              size="icon" 
              onClick={() => fetchData(true)} 
              disabled={loading}
            >
              <RefreshCw className={`h-4 w-4 ${loading ? 'animate-spin' : ''}`} />
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
                {filteredActors && filteredActors.length > 0 
                  ? `Showing ${filteredActors.length} of ${actors.length} threat actors`
                  : 'No matching threat actors found'
                }
              </TableCaption>
              <TableHeader>
                <TableRow>
                  <TableHead className="w-[200px]">Name</TableHead>
                  <TableHead>Type</TableHead>
                  <TableHead>Origin</TableHead>
                  <TableHead>Last Updated</TableHead>
                  <TableHead className="text-right">Actions</TableHead>
                </TableRow>
              </TableHeader>
              <TableBody>
                {filteredActors && filteredActors.length > 0 ? (
                  filteredActors.map((actor) => (
                    <React.Fragment key={actor.actor_id}>
                      <TableRow>
                        <TableCell className="font-medium">
                          <div className="flex items-center">
                            <span>{actor.name}</span>
                            <Button
                              variant="ghost"
                              size="icon"
                              className="h-7 w-7 ml-1"
                              onClick={(e) => {
                                e.stopPropagation();
                                toggleRowExpansion(actor.actor_id);
                              }}
                              title="View full details"
                            >
                              <ExternalLink className="h-3.5 w-3.5" />
                            </Button>
                          </div>
                        </TableCell>
                        <TableCell>
                          {actor.adversary_type || 'Unknown'}
                        </TableCell>
                        <TableCell>
                          <div className="flex flex-wrap gap-1">
                            {actor.origins && actor.origins.length > 0 ? (
                              actor.origins.map((origin, index) => (
                                <Badge key={index} variant="outline" className="flex items-center gap-1">
                                  <Globe className="h-3 w-3" />
                                  {origin}
                                </Badge>
                              ))
                            ) : (
                              'Unknown'
                            )}
                          </div>
                        </TableCell>
                        <TableCell>{formatDate(actor.last_update_date)}</TableCell>
                        <TableCell className="text-right">
                          <Button
                            variant="ghost"
                            size="sm"
                            onClick={() => toggleRowExpansion(actor.actor_id)}
                          >
                            {expandedRows.has(actor.actor_id) ? (
                              <ChevronUp className="h-4 w-4 mr-1" />
                            ) : (
                              <ChevronDown className="h-4 w-4 mr-1" />
                            )}
                            {expandedRows.has(actor.actor_id) ? 'Hide Details' : 'Show Details'}
                          </Button>
                        </TableCell>
                      </TableRow>
                      {expandedRows.has(actor.actor_id) && (
                        <TableRow>
                          <TableCell colSpan={5} className="p-4 bg-gray-50">
                            <div className="text-sm">
                              <div className="flex justify-between items-start mb-4">
                                <h4 className="font-semibold">Details</h4>
                                <Button
                                  size="sm"
                                  variant="outline"
                                  className="text-blue-600 hover:text-blue-800"
                                  onClick={() => {
                                    // This would normally link to a full report page
                                    // For demo purposes, we're just toggling the expanded view
                                    window.open(`https://intelligence.crowdstrike.com/actors/${actor.actor_id}`, '_blank');
                                  }}
                                >
                                  <ExternalLink className="h-4 w-4 mr-1" />
                                  View Full Report
                                </Button>
                              </div>
                              
                              {actor.description && (
                                <div className="mb-3">
                                  <h5 className="font-medium text-gray-700 mb-1">Description</h5>
                                  <p className="text-gray-600">{actor.description}</p>
                                </div>
                              )}
                              
                              {actor.capabilities && actor.capabilities.length > 0 && (
                                <div className="mb-3">
                                  <h5 className="font-medium text-gray-700 mb-1">Capabilities</h5>
                                  <ul className="list-disc pl-5 text-gray-600">
                                    {actor.capabilities.map((capability, index) => (
                                      <li key={index}>{capability}</li>
                                    ))}
                                  </ul>
                                </div>
                              )}
                              
                              {actor.motivations && actor.motivations.length > 0 && (
                                <div className="mb-3">
                                  <h5 className="font-medium text-gray-700 mb-1">Motivations</h5>
                                  <ul className="list-disc pl-5 text-gray-600">
                                    {actor.motivations.map((motivation, index) => (
                                      <li key={index}>{motivation}</li>
                                    ))}
                                  </ul>
                                </div>
                              )}
                              
                              {actor.objectives && actor.objectives.length > 0 && (
                                <div className="mb-3">
                                  <h5 className="font-medium text-gray-700 mb-1">Objectives</h5>
                                  <ul className="list-disc pl-5 text-gray-600">
                                    {actor.objectives.map((objective, index) => (
                                      <li key={index}>{objective}</li>
                                    ))}
                                  </ul>
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