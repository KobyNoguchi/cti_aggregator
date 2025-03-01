import React, { useState, useEffect } from 'react';
import {
  Box,
  Input,
  Select,
  Text,
  Heading,
  Link,
  VStack,
  Flex,
  Badge,
  Spinner,
  Alert,
  Icon,
  useColorModeValue
} from '@chakra-ui/react';
import { ExternalLinkIcon } from '@chakra-ui/icons';

const IntelligenceFeed = () => {
  const [articles, setArticles] = useState([]);
  const [loading, setLoading] = useState(true);
  const [searchTerm, setSearchTerm] = useState('');
  const [selectedSource, setSelectedSource] = useState('all');
  const [error, setError] = useState(null);

  // Use color mode values
  const cardBg = useColorModeValue('white', 'gray.800');
  const cardBorder = useColorModeValue('gray.200', 'gray.600');
  const sourceBadgeBg = useColorModeValue('blue.100', 'blue.900');
  const sourceBadgeColor = useColorModeValue('blue.800', 'blue.200');

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
      } catch (error) {
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

  const handleSearchChange = (e) => {
    setSearchTerm(e.target.value);
  };

  const handleSourceChange = (e) => {
    setSelectedSource(e.target.value);
  };

  if (loading) return (
    <Flex justify="center" align="center" h="100%">
      <Spinner size="xl" color="blue.500" thickness="4px" />
    </Flex>
  );
  
  if (error) return (
    <Alert status="error" borderRadius="md">
      {error}
    </Alert>
  );

  // Get unique sources for the filter dropdown
  const sources = ['all', ...new Set(articles.map(article => article.source))];

  return (
    <Box h="100%">
      <Flex mb={4} gap={2}>
        <Input
          placeholder="Search articles..."
          value={searchTerm}
          onChange={handleSearchChange}
          size="sm"
          flex="1"
        />
        <Select
          value={selectedSource}
          onChange={handleSourceChange}
          size="sm"
          width="150px"
        >
          {sources.map(source => (
            <option key={source} value={source}>
              {source === 'all' ? 'All Sources' : source}
            </option>
          ))}
        </Select>
      </Flex>

      <Box 
        overflowY="auto" 
        h="calc(100% - 40px)"
        pr={2}
      >
        {filteredArticles.length > 0 ? (
          <VStack spacing={4} align="stretch">
            {filteredArticles.map((article) => (
              <Box
                key={article.id}
                p={4}
                borderWidth="1px"
                borderRadius="md"
                borderColor={cardBorder}
                bg={cardBg}
                boxShadow="sm"
                transition="all 0.2s"
                _hover={{ boxShadow: 'md' }}
              >
                <Flex justify="space-between" align="center" mb={2}>
                  <Badge 
                    bg={sourceBadgeBg} 
                    color={sourceBadgeColor}
                    borderRadius="full"
                    px={2}
                    py={0.5}
                    fontSize="xs"
                  >
                    {article.source || 'Unknown'}
                  </Badge>
                  <Text fontSize="xs" color="gray.500">
                    {article.published_date ? new Date(article.published_date).toLocaleDateString() : 'Unknown date'}
                  </Text>
                </Flex>
                
                <Heading size="sm" mb={2}>
                  <Link 
                    href={article.url} 
                    isExternal
                    color="blue.600"
                    _hover={{ textDecoration: 'underline' }}
                  >
                    {article.title || 'No title'}
                    <Icon as={ExternalLinkIcon} mx="2px" />
                  </Link>
                </Heading>
                
                {article.summary ? (
                  <Text fontSize="sm" color="gray.700">
                    {article.summary.length > 200 
                      ? `${article.summary.substring(0, 200)}...` 
                      : article.summary}
                  </Text>
                ) : (
                  <Text fontSize="sm" color="gray.500">No summary available</Text>
                )}
              </Box>
            ))}
          </VStack>
        ) : (
          <Flex 
            justify="center" 
            align="center" 
            h="100%" 
            color="gray.500"
          >
            <Text>No articles found matching your criteria.</Text>
          </Flex>
        )}
      </Box>
    </Box>
  );
};

export default IntelligenceFeed; 