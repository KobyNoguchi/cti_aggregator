"use client"

import React, { useState, useEffect } from 'react'
import { fetchCrowdStrikeActors, CrowdStrikeActor } from '@/lib/api'
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
  Globe
} from 'lucide-react'
import { Badge } from '@/components/ui/badge'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Alert, AlertDescription } from '@/components/ui/alert'

export default function CrowdStrikeActorsTable() {
  const [actors, setActors] = useState<CrowdStrikeActor[]>([]);
  const [filteredActors, setFilteredActors] = useState<CrowdStrikeActor[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [searchTerm, setSearchTerm] = useState('');
  const [selectedAdversaryType, setSelectedAdversaryType] = useState('all');
  const [selectedOrigin, setSelectedOrigin] = useState('all');
  const [adversaryTypes, setAdversaryTypes] = useState<string[]>([]);
  const [origins, setOrigins] = useState<string[]>([]);
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

  // Filter actors when search term or selected filters change
  useEffect(() => {
    filterActors();
  }, [searchTerm, selectedAdversaryType, selectedOrigin, actors]);

  // Fetch data from the API
  const fetchData = async () => {
    try {
      setLoading(true);
      const data = await fetchCrowdStrikeActors();
      setActors(data);
      
      // Extract unique adversary types for filter dropdown
      const uniqueAdversaryTypes = [...new Set(data.map(actor => actor.adversary_type))].filter(Boolean).sort();
      setAdversaryTypes(uniqueAdversaryTypes as string[]);
      
      // Extract unique origins for filter dropdown
      const allOrigins = data.flatMap(actor => actor.origins || []);
      const uniqueOrigins = [...new Set(allOrigins)].filter(Boolean).sort();
      setOrigins(uniqueOrigins as string[]);
      
      setError(null);
    } catch (err) {
      setError('Failed to fetch CrowdStrike actor data. Please try again later.');
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  // Filter actors based on search term and selected filters
  const filterActors = () => {
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
        (actor.capabilities && actor.capabilities.some(capability => capability.toLowerCase().includes(search))) ||
        (actor.motivations && actor.motivations.some(motivation => motivation.toLowerCase().includes(search))) ||
        (actor.objectives && actor.objectives.some(objective => objective.toLowerCase().includes(search)))
      );
    }
    
    setFilteredActors(filtered);
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
  const toggleRowExpansion = (actorId: string) => {
    const newExpandedRows = new Set(expandedRows);
    if (newExpandedRows.has(actorId)) {
      newExpandedRows.delete(actorId);
    } else {
      newExpandedRows.add(actorId);
    }
    setExpandedRows(newExpandedRows);
  };

  return (
    <Card className="w-full">
      <CardHeader className="pb-2">
        <CardTitle className="text-xl font-semibold">CrowdStrike Threat Actors</CardTitle>
        <div className="flex flex-col sm:flex-row justify-between gap-4 mt-4">
          <div className="flex items-center gap-2 w-full sm:w-auto">
            <Search className="w-4 h-4 text-gray-500" />
            <Input
              placeholder="Search threat actors..."
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
                <SelectValue placeholder="All Adversary Types" />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="all">All Adversary Types</SelectItem>
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
                <SelectValue placeholder="All Origins" />
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
                {filteredActors.length > 0 
                  ? `Showing ${filteredActors.length} of ${actors.length} threat actors`
                  : 'No matching threat actors found'
                }
              </TableCaption>
              <TableHeader>
                <TableRow>
                  <TableHead className="w-[50px]"></TableHead>
                  <TableHead>Name</TableHead>
                  <TableHead className="hidden md:table-cell">Type</TableHead>
                  <TableHead className="hidden md:table-cell">Origins</TableHead>
                  <TableHead className="hidden md:table-cell">Last Updated</TableHead>
                </TableRow>
              </TableHeader>
              <TableBody>
                {filteredActors.length > 0 ? (
                  filteredActors.map((actor) => (
                    <React.Fragment key={actor.actor_id}>
                      <TableRow
                        className="cursor-pointer"
                        onClick={() => toggleRowExpansion(actor.actor_id)}
                      >
                        <TableCell>
                          {expandedRows.has(actor.actor_id) ? (
                            <ChevronUp className="h-4 w-4" />
                          ) : (
                            <ChevronDown className="h-4 w-4" />
                          )}
                        </TableCell>
                        <TableCell className="font-medium">
                          {actor.name}
                        </TableCell>
                        <TableCell className="hidden md:table-cell">
                          {actor.adversary_type || 'Unknown'}
                        </TableCell>
                        <TableCell className="hidden md:table-cell">
                          <div className="flex flex-wrap gap-1">
                            {actor.origins && actor.origins.length > 0 ? (
                              actor.origins.slice(0, 2).map((origin, index) => (
                                <Badge key={index} variant="outline" className="bg-blue-50 text-blue-700 border-blue-200 flex items-center gap-1">
                                  <Globe className="h-3 w-3" />
                                  {origin}
                                </Badge>
                              ))
                            ) : (
                              <span className="text-gray-500 text-sm">Unknown</span>
                            )}
                            {actor.origins && actor.origins.length > 2 && (
                              <Badge variant="outline" className="bg-gray-50 text-gray-700">
                                +{actor.origins.length - 2} more
                              </Badge>
                            )}
                          </div>
                        </TableCell>
                        <TableCell className="hidden md:table-cell">
                          {formatDate(actor.last_update_date)}
                        </TableCell>
                      </TableRow>
                      {expandedRows.has(actor.actor_id) && (
                        <TableRow>
                          <TableCell colSpan={5} className="p-4 bg-gray-50">
                            <div className="space-y-4">
                              <div>
                                <h4 className="text-sm font-semibold mb-1">Description</h4>
                                <p className="text-sm text-gray-700">{actor.description || 'No description available'}</p>
                              </div>
                              
                              <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                                <div>
                                  <h4 className="text-sm font-semibold mb-1">Capabilities</h4>
                                  <div className="flex flex-wrap gap-1">
                                    {actor.capabilities && actor.capabilities.length > 0 ? (
                                      actor.capabilities.map((capability, index) => (
                                        <Badge key={index} variant="outline" className="bg-red-50 text-red-700 border-red-200">
                                          {capability}
                                        </Badge>
                                      ))
                                    ) : (
                                      <span className="text-gray-500 text-sm">None identified</span>
                                    )}
                                  </div>
                                </div>
                                
                                <div>
                                  <h4 className="text-sm font-semibold mb-1">Motivations</h4>
                                  <div className="flex flex-wrap gap-1">
                                    {actor.motivations && actor.motivations.length > 0 ? (
                                      actor.motivations.map((motivation, index) => (
                                        <Badge key={index} variant="outline" className="bg-purple-50 text-purple-700 border-purple-200">
                                          {motivation}
                                        </Badge>
                                      ))
                                    ) : (
                                      <span className="text-gray-500 text-sm">None identified</span>
                                    )}
                                  </div>
                                </div>
                                
                                <div>
                                  <h4 className="text-sm font-semibold mb-1">Objectives</h4>
                                  <div className="flex flex-wrap gap-1">
                                    {actor.objectives && actor.objectives.length > 0 ? (
                                      actor.objectives.map((objective, index) => (
                                        <Badge key={index} variant="outline" className="bg-green-50 text-green-700 border-green-200">
                                          {objective}
                                        </Badge>
                                      ))
                                    ) : (
                                      <span className="text-gray-500 text-sm">None identified</span>
                                    )}
                                  </div>
                                </div>
                              </div>
                              
                              <div>
                                <h4 className="text-sm font-semibold mb-1">Origins</h4>
                                <div className="flex flex-wrap gap-1">
                                  {actor.origins && actor.origins.length > 0 ? (
                                    actor.origins.map((origin, index) => (
                                      <Badge key={index} variant="outline" className="bg-blue-50 text-blue-700 border-blue-200 flex items-center gap-1">
                                        <Globe className="h-3 w-3" />
                                        {origin}
                                      </Badge>
                                    ))
                                  ) : (
                                    <span className="text-gray-500 text-sm">Unknown</span>
                                  )}
                                </div>
                              </div>
                              
                              <div>
                                <h4 className="text-sm font-semibold mb-1">Last Updated</h4>
                                <p className="text-sm">{formatDate(actor.last_update_date)}</p>
                              </div>
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