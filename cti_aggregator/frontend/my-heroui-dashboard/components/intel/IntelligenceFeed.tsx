"use client";

import React, { useState, useEffect } from 'react';

interface Article {
  id: string;
  title?: string;
  summary?: string;
  url?: string;
  source?: string;
  published_date?: string;
}

const IntelligenceFeed: React.FC<{
  searchTerm?: string;
  dateRange?: [Date | null, Date | null];
}> = ({ searchTerm: externalSearchTerm, dateRange }) => {
  const [articles, setArticles] = useState<Article[]>([]);
  const [loading, setLoading] = useState(true);
  const [searchTerm, setSearchTerm] = useState('');
  const [selectedSource, setSelectedSource] = useState('all');
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (externalSearchTerm !== undefined) {
      setSearchTerm(externalSearchTerm);
    }
  }, [externalSearchTerm]);

  useEffect(() => {
    const fetchArticles = async () => {
      try {
        setLoading(true);
        console.log('Fetching intelligence articles from API...');
        const response = await fetch('http://localhost:8000/api/intelligence/');
        
        if (!response.ok) {
          throw new Error(`HTTP error! status: ${response.status}`);
        }
        
        const data = await response.json();
        console.log('Intelligence articles fetched successfully:', data);
        setArticles(data);
        setLoading(false);
      } catch (error: any) {
        console.error("Error fetching intelligence articles:", error);
        setError(`Failed to load intelligence feed: ${error.message}`);
        setLoading(false);
      }
    };

    fetchArticles();
  }, []);

  // Filter articles based on search term and selected source
  const filteredArticles = articles.filter(article => {
    const matchesSearch = 
      article.title?.toLowerCase().includes(searchTerm.toLowerCase()) ||
      (article.summary && article.summary.toLowerCase().includes(searchTerm.toLowerCase()));
    
    const matchesSource = selectedSource === 'all' || article.source === selectedSource;
    
    return matchesSearch && matchesSource;
  });

  const handleSearchChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    setSearchTerm(e.target.value);
  };

  const handleSourceChange = (e: React.ChangeEvent<HTMLSelectElement>) => {
    setSelectedSource(e.target.value);
  };

  if (loading) return (
    <div className="flex justify-center items-center h-full">
      <div className="h-8 w-8 animate-spin rounded-full border-b-2 border-primary"></div>
    </div>
  );
  
  if (error) return (
    <div className="bg-red-50 dark:bg-red-900/20 p-4 rounded-md border border-red-200 dark:border-red-800">
      <p className="text-red-700 dark:text-red-400">{error}</p>
    </div>
  );

  // Get unique sources for the filter dropdown
  const sources = ['all', ...new Set(articles.map(article => article.source).filter(Boolean) as string[])];

  return (
    <div className="h-full">
      <div className="flex mb-4 gap-2">
        <div className="relative flex-1">
          <input
            type="text"
            placeholder="Search articles..."
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
          value={selectedSource}
          onChange={handleSourceChange}
          className="px-3 py-2 border border-gray-300 rounded-md w-[150px] dark:bg-gray-800 dark:border-gray-700 dark:text-white"
        >
          {sources.map(source => (
            <option key={source} value={source}>
              {source === 'all' ? 'All Sources' : source}
            </option>
          ))}
        </select>
      </div>

      <div className="overflow-y-auto h-[calc(100%-40px)] pr-2">
        {filteredArticles.length > 0 ? (
          <div className="space-y-4">
            {filteredArticles.map((article) => (
              <div key={article.id} className="border rounded-md p-4 transition-all hover:shadow-md dark:bg-gray-800 dark:border-gray-700">
                <div className="flex justify-between items-center mb-2">
                  <span className="inline-flex items-center rounded-full bg-blue-100 px-2.5 py-0.5 text-xs font-medium text-blue-800 dark:bg-blue-900 dark:text-blue-200">
                    {article.source || 'Unknown'}
                  </span>
                  <span className="text-xs text-gray-500 dark:text-gray-400">
                    {article.published_date ? new Date(article.published_date).toLocaleDateString() : 'Unknown date'}
                  </span>
                </div>
                
                <h3 className="text-sm font-semibold mb-2">
                  <a 
                    href={article.url} 
                    target="_blank"
                    rel="noopener noreferrer"
                    className="text-blue-600 hover:underline flex items-center dark:text-blue-400"
                  >
                    {article.title || 'No title'}
                    <svg className="h-4 w-4 ml-1" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M10 6H6a2 2 0 00-2 2v10a2 2 0 002 2h10a2 2 0 002-2v-4M14 4h6m0 0v6m0-6L10 14" />
                    </svg>
                  </a>
                </h3>
                
                {article.summary ? (
                  <p className="text-sm text-gray-700 dark:text-gray-300">
                    {article.summary.length > 200 
                      ? `${article.summary.substring(0, 200)}...` 
                      : article.summary}
                  </p>
                ) : (
                  <p className="text-sm text-gray-500 dark:text-gray-400">No summary available</p>
                )}
              </div>
            ))}
          </div>
        ) : (
          <div className="flex justify-center items-center h-full text-gray-500 dark:text-gray-400">
            <p>No articles found matching your criteria.</p>
          </div>
        )}
      </div>
    </div>
  );
};

export default IntelligenceFeed; 