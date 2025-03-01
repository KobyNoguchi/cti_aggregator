import React, { useState, useEffect } from 'react';
import './IntelligenceFeed.css';

const IntelligenceFeed = () => {
  const [articles, setArticles] = useState([]);
  const [loading, setLoading] = useState(true);
  const [searchTerm, setSearchTerm] = useState('');
  const [selectedSource, setSelectedSource] = useState('all');
  const [error, setError] = useState(null);

  useEffect(() => {
    const fetchArticles = async () => {
      try {
        setLoading(true);
        const response = await fetch('http://localhost:8000/api/intelligence/');
        
        if (!response.ok) {
          throw new Error(`HTTP error! status: ${response.status}`);
        }
        
        const data = await response.json();
        setArticles(data);
        setLoading(false);
      } catch (error) {
        console.error("Error fetching intelligence articles:", error);
        setError("Failed to load intelligence feed. Please try again later.");
        setLoading(false);
      }
    };

    fetchArticles();
  }, []);

  // Filter articles based on search term and selected source
  const filteredArticles = articles.filter(article => {
    const matchesSearch = 
      article.title.toLowerCase().includes(searchTerm.toLowerCase()) ||
      (article.summary && article.summary.toLowerCase().includes(searchTerm.toLowerCase()));
    
    const matchesSource = selectedSource === 'all' || article.source === selectedSource;
    
    return matchesSearch && matchesSource;
  });

  const handleSearchChange = (e) => {
    setSearchTerm(e.target.value);
  };

  const handleSourceChange = (e) => {
    setSelectedSource(e.target.value);
  };

  if (loading) return <div className="loading">Loading intelligence feed...</div>;
  if (error) return <div className="error">{error}</div>;

  // Get unique sources for the filter dropdown
  const sources = ['all', ...new Set(articles.map(article => article.source))];

  return (
    <div className="intelligence-feed">
      <div className="feed-controls">
        <input
          type="text"
          placeholder="Search intelligence articles..."
          value={searchTerm}
          onChange={handleSearchChange}
          className="search-input"
        />
        
        <select 
          value={selectedSource} 
          onChange={handleSourceChange}
          className="source-select"
        >
          {sources.map(source => (
            <option key={source} value={source}>
              {source === 'all' ? 'All Sources' : source}
            </option>
          ))}
        </select>
      </div>
      
      <div className="articles-container">
        {filteredArticles.length > 0 ? (
          filteredArticles.map(article => (
            <div key={article.id} className="article-card">
              <div className="article-source">{article.source}</div>
              <h3 className="article-title">
                <a href={article.url} target="_blank" rel="noopener noreferrer">
                  {article.title}
                </a>
              </h3>
              <div className="article-date">
                {new Date(article.published_date).toLocaleDateString()}
              </div>
              {article.summary && (
                <p className="article-summary">{article.summary}</p>
              )}
            </div>
          ))
        ) : (
          <div className="no-results">No intelligence articles found.</div>
        )}
      </div>
    </div>
  );
};

export default IntelligenceFeed; 