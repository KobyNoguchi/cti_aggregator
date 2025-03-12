import React, { useState, useEffect } from 'react';
import {
  Box,
  Input,
  Select,
  Text,
  Heading,
  VStack,
  Flex,
  Badge,
  Spinner,
  Alert,
  Accordion,
  AccordionItem,
  AccordionButton,
  AccordionPanel,
  AccordionIcon,
  Tag,
  Wrap,
  WrapItem,
  useColorModeValue
} from '@chakra-ui/react';

const CrowdStrikeIntelPanel = () => {
  const [actors, setActors] = useState([]);
  const [loading, setLoading] = useState(true);
  const [searchTerm, setSearchTerm] = useState('');
  const [selectedType, setSelectedType] = useState('all');
  const [error, setError] = useState(null);

  // Use color mode values
  const cardBg = useColorModeValue('white', 'gray.800');
  const cardBorder = useColorModeValue('gray.200', 'gray.600');
  const headerBg = useColorModeValue('red.100', 'red.900');
  const headerColor = useColorModeValue('red.800', 'red.200');
  const tagBg = useColorModeValue('orange.100', 'orange.900');
  const tagColor = useColorModeValue('orange.800', 'orange.200');

  useEffect(() => {
    const fetchActors = async () => {
      try {
        setLoading(true);
        console.log('Fetching CrowdStrike threat intelligence...');
        
        // Add a timestamp to prevent caching
        const timestamp = new Date().getTime();
        const response = await fetch(`http://localhost:8000/api/crowdstrike-intel/?t=${timestamp}`);
        
        if (!response.ok) {
          throw new Error(`HTTP error! status: ${response.status}`);
        }
        
        const data = await response.json();
        console.log('CrowdStrike threat intelligence fetched successfully:', data);
        
        // Check if data is an array
        if (!Array.isArray(data)) {
          console.error('Expected array but got:', typeof data);
          setError('Invalid data format received from API');
          setLoading(false);
          return;
        }
        
        // Check if data has the expected structure
        if (data.length > 0) {
          console.log('Sample data item:', data[0]);
        } else {
          console.log('No data items returned from API');
        }
        
        setActors(data);
        setLoading(false);
      } catch (error) {
        console.error("Error fetching CrowdStrike threat intelligence:", error);
        setError(`Failed to load threat intelligence: ${error.message}`);
        setLoading(false);
      }
    };

    fetchActors();
  }, []);

  // Filter actors based on search term and selected type
  const filteredActors = actors.filter(actor => {
    console.log('Filtering actor:', actor.name, actor.adversary_type);
    
    const matchesSearch = 
      actor.name?.toLowerCase().includes(searchTerm.toLowerCase()) ||
      (actor.description && actor.description.toLowerCase().includes(searchTerm.toLowerCase()));
    
    const matchesType = selectedType === 'all' || actor.adversary_type === selectedType;
    
    return matchesSearch && matchesType;
  });

  console.log('Filtered actors count:', filteredActors.length);

  const handleSearchChange = (e) => {
    setSearchTerm(e.target.value);
  };

  const handleTypeChange = (e) => {
    setSelectedType(e.target.value);
  };

  if (loading) return (
    <Flex justify="center" align="center" h="100%">
      <Spinner size="xl" color="red.500" thickness="4px" />
    </Flex>
  );
  
  if (error) return (
    <Alert status="error" borderRadius="md">
      {error}
    </Alert>
  );

  // Get unique actor types for the filter dropdown
  const actorTypes = ['all', ...new Set(actors.map(actor => actor.adversary_type).filter(Boolean))];

  // Function to render tags from arrays
  const renderTags = (items, colorScheme = 'orange') => {
    console.log('Rendering tags for:', items, 'Type:', typeof items);
    
    // Handle null or undefined
    if (!items) {
      return <Text fontSize="sm">None specified</Text>;
    }
    
    // Handle string that might be JSON
    if (typeof items === 'string') {
      try {
        items = JSON.parse(items);
        console.log('Parsed JSON string to:', items);
      } catch (e) {
        console.log('Failed to parse as JSON, treating as single item');
        items = [items]; // Treat as a single item
      }
    }
    
    // Ensure items is an array
    if (!Array.isArray(items)) {
      console.log('Items is not an array, converting to array');
      items = [items]; // Convert to array with single item
    }
    
    // Check if array is empty
    if (items.length === 0) {
      return <Text fontSize="sm">None specified</Text>;
    }
    
    return (
      <Wrap spacing={2} mt={1}>
        {items.map((item, idx) => (
          <WrapItem key={idx}>
            <Tag 
              size="sm" 
              bg={tagBg} 
              color={tagColor}
              borderRadius="full"
              wordBreak="break-word"
              whiteSpace="normal"
            >
              {item}
            </Tag>
          </WrapItem>
        ))}
      </Wrap>
    );
  };

  return (
    <Box h="100%">
      <Flex mb={4} gap={2}>
        <Input
          placeholder="Search threat actors..."
          value={searchTerm}
          onChange={handleSearchChange}
          size="sm"
          flex="1"
        />
        <Select
          value={selectedType}
          onChange={handleTypeChange}
          size="sm"
          width="150px"
        >
          {actorTypes.map(type => (
            <option key={type} value={type}>
              {type === 'all' ? 'All Types' : type}
            </option>
          ))}
        </Select>
      </Flex>

      <Box 
        overflowY="auto" 
        h="calc(100% - 40px)"
        pr={2}
      >
        {filteredActors.length > 0 ? (
          <Accordion allowMultiple>
            {filteredActors.map((actor) => (
              <AccordionItem 
                key={actor.actor_id}
                my={2}
                border="1px"
                borderColor={cardBorder}
                borderRadius="md"
                bg={cardBg}
              >
                <h2>
                  <AccordionButton py={3}>
                    <Box flex="1" textAlign="left">
                      <Flex justify="space-between" align="center" flexWrap="wrap" gap={2}>
                        <Heading size="sm" wordBreak="break-word">{actor.name}</Heading>
                        <Badge 
                          bg={headerBg} 
                          color={headerColor}
                          borderRadius="full"
                          px={2}
                          py={0.5}
                          fontSize="xs"
                        >
                          {actor.adversary_type || 'Unknown'}
                        </Badge>
                      </Flex>
                    </Box>
                    <AccordionIcon />
                  </AccordionButton>
                </h2>
                <AccordionPanel pb={4}>
                  {actor.description && (
                    <Box mb={3}>
                      <Text fontSize="sm" fontWeight="bold">Description:</Text>
                      <Text fontSize="sm" wordBreak="break-word">{actor.description}</Text>
                    </Box>
                  )}

                  <Box mb={3}>
                    <Text fontSize="sm" fontWeight="bold">Origins:</Text>
                    {renderTags(actor.origins)}
                  </Box>

                  <Box mb={3}>
                    <Text fontSize="sm" fontWeight="bold">Capabilities:</Text>
                    {renderTags(actor.capabilities)}
                  </Box>

                  <Box mb={3}>
                    <Text fontSize="sm" fontWeight="bold">Motivations:</Text>
                    {renderTags(actor.motivations)}
                  </Box>

                  <Box mb={3}>
                    <Text fontSize="sm" fontWeight="bold">Objectives:</Text>
                    {renderTags(actor.objectives)}
                  </Box>

                  <Text fontSize="xs" color="gray.500">
                    Last updated: {actor.last_update_date ? new Date(actor.last_update_date).toLocaleString() : 'Unknown'}
                  </Text>
                </AccordionPanel>
              </AccordionItem>
            ))}
          </Accordion>
        ) : (
          <Flex 
            justify="center" 
            align="center" 
            h="100%" 
            color="gray.500"
          >
            <Text>No threat actors found matching your criteria.</Text>
          </Flex>
        )}
      </Box>
    </Box>
  );
};

export default CrowdStrikeIntelPanel; 