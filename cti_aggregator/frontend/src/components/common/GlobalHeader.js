import React, { useState } from 'react';
import {
  Box,
  Flex,
  Heading,
  Input,
  InputGroup,
  InputLeftElement,
  Spacer,
  HStack,
  useColorModeValue,
  Button,
  Popover,
  PopoverTrigger,
  PopoverContent,
  PopoverBody,
  PopoverArrow,
  useDisclosure,
  Icon,
} from '@chakra-ui/react';
import { SearchIcon, CalendarIcon } from '@chakra-ui/icons';
import SimpleDateRangePicker from './SimpleDateRangePicker';

/**
 * GlobalHeader component that provides a fixed header with search and date filter capabilities
 * This component can be used across different modules to maintain consistency
 */
const GlobalHeader = ({ 
  title, 
  bg = 'blue.500',
  color = 'white',
  onSearch,
  onDateChange,
  showSearch = true,
  showDateFilter = true,
}) => {
  const [searchTerm, setSearchTerm] = useState('');
  const [selectedDateRange, setSelectedDateRange] = useState([new Date(), new Date()]);
  const { isOpen, onOpen, onClose } = useDisclosure();

  const handleSearch = (e) => {
    const value = e.target.value;
    setSearchTerm(value);
    if (onSearch) onSearch(value);
  };

  const handleDateChange = (dates) => {
    setSelectedDateRange(dates);
    if (onDateChange) onDateChange(dates);
  };

  const handleClearFilters = () => {
    setSearchTerm('');
    setSelectedDateRange([new Date(), new Date()]);
    if (onSearch) onSearch('');
    if (onDateChange) onDateChange([new Date(), new Date()]);
  };

  return (
    <Box 
      position="sticky"
      top="0"
      zIndex="sticky"
      width="full"
      bg={bg}
      color={color}
      py={3}
      px={4}
      boxShadow="md"
    >
      <Flex align="center">
        <Heading as="h3" size="md" noOfLines={1}>
          {title}
        </Heading>
        <Spacer />
        <HStack spacing={3}>
          {showSearch && (
            <InputGroup size="sm" w={{ base: '120px', md: '200px' }}>
              <InputLeftElement pointerEvents="none">
                <SearchIcon color="gray.300" />
              </InputLeftElement>
              <Input
                placeholder="Search..."
                bg="white"
                color="gray.800"
                value={searchTerm}
                onChange={handleSearch}
                borderRadius="md"
                _placeholder={{ color: 'gray.400' }}
              />
            </InputGroup>
          )}

          {showDateFilter && (
            <Popover
              isOpen={isOpen}
              onOpen={onOpen}
              onClose={onClose}
              placement="bottom-end"
              closeOnBlur={true}
            >
              <PopoverTrigger>
                <Button 
                  size="sm" 
                  leftIcon={<CalendarIcon />}
                  variant="solid"
                  colorScheme="whiteAlpha"
                >
                  Date Filter
                </Button>
              </PopoverTrigger>
              <PopoverContent 
                width="fit-content" 
                p={2}
                bg="white"
                color="gray.800"
              >
                <PopoverArrow />
                <PopoverBody>
                  <SimpleDateRangePicker
                    selectedDates={selectedDateRange}
                    onDateChange={handleDateChange}
                  />
                  <Flex mt={2} justify="space-between">
                    <Button size="sm" onClick={onClose} colorScheme="blue">
                      Apply
                    </Button>
                    <Button size="sm" variant="ghost" onClick={handleClearFilters}>
                      Clear
                    </Button>
                  </Flex>
                </PopoverBody>
              </PopoverContent>
            </Popover>
          )}
        </HStack>
      </Flex>
    </Box>
  );
};

export default GlobalHeader; 