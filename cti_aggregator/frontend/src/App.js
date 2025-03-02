import React, { useState } from "react";
import { BrowserRouter as Router, Routes, Route } from "react-router-dom";
import { 
  Box, 
  Flex, 
  Heading, 
  Container, 
  HStack, 
  Input, 
  InputGroup, 
  InputLeftElement,
  Button,
  useDisclosure,
  Popover,
  PopoverTrigger,
  PopoverContent,
  PopoverArrow,
  PopoverBody,
  Spacer
} from "@chakra-ui/react";
import { SearchIcon, CalendarIcon } from "@chakra-ui/icons";
import Dashboard from "./components/Dashboard";
import VulnerabilityTable from "./components/VulnerabilityTable";
import SimpleDateRangePicker from "./components/common/SimpleDateRangePicker";
import "./App.css";

function App() {
  const bgColor = "gray.50";
  const headerBgColor = "brand.500";
  const headerColor = "white";
  const [globalSearchTerm, setGlobalSearchTerm] = useState('');
  const [globalDateRange, setGlobalDateRange] = useState([new Date(), new Date()]);
  const { isOpen, onOpen, onClose } = useDisclosure();

  // Handle global search changes
  const handleGlobalSearch = (e) => {
    setGlobalSearchTerm(e.target.value);
    // Store in session storage to persist across page refreshes
    sessionStorage.setItem('globalSearchTerm', e.target.value);
  };

  // Handle global date range changes
  const handleGlobalDateChange = (dates) => {
    setGlobalDateRange(dates);
    // Store in session storage as ISO strings
    sessionStorage.setItem('globalDateRange', JSON.stringify(dates.map(d => d ? d.toISOString() : null)));
  };

  // Clear all filters
  const clearAllFilters = () => {
    setGlobalSearchTerm('');
    setGlobalDateRange([new Date(), new Date()]);
    sessionStorage.removeItem('globalSearchTerm');
    sessionStorage.removeItem('globalDateRange');
  };

  return (
    <Router>
      <Flex direction="column" minH="100vh" bg={bgColor}>
        {/* Fixed Header */}
        <Box 
          as="header" 
          bg={headerBgColor} 
          color={headerColor} 
          py={4} 
          px={6} 
          position="sticky"
          top="0"
          zIndex="1000"
          boxShadow="md"
        >
          <Container maxW="container.xl">
            <Flex align="center">
              <Heading size="lg">CTI Aggregator</Heading>
              <Spacer />
              <HStack spacing={4}>
                {/* Global Search */}
                <InputGroup size="sm" w={{ base: "120px", md: "300px" }}>
                  <InputLeftElement pointerEvents="none">
                    <SearchIcon color="gray.300" />
                  </InputLeftElement>
                  <Input
                    placeholder="Search across all modules..."
                    bg="white"
                    color="gray.800"
                    value={globalSearchTerm}
                    onChange={handleGlobalSearch}
                    borderRadius="md"
                    _placeholder={{ color: "gray.400" }}
                  />
                </InputGroup>

                {/* Date Range Picker */}
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
                        selectedDates={globalDateRange}
                        onDateChange={handleGlobalDateChange}
                      />
                      <Flex mt={2} justify="space-between">
                        <Button size="sm" onClick={onClose} colorScheme="blue">
                          Apply
                        </Button>
                        <Button size="sm" variant="ghost" onClick={clearAllFilters}>
                          Clear All Filters
                        </Button>
                      </Flex>
                    </PopoverBody>
                  </PopoverContent>
                </Popover>
              </HStack>
            </Flex>
          </Container>
        </Box>
        
        {/* Main Content */}
        <Box flex="1" p={4}>
          <Container maxW="container.xl" h="100%">
            <Routes>
              <Route 
                path="/" 
                element={
                  <Dashboard 
                    globalSearchTerm={globalSearchTerm} 
                    globalDateRange={globalDateRange} 
                  />
                } 
              />
              <Route 
                path="/legacy" 
                element={
                  <VulnerabilityTable 
                    globalSearchTerm={globalSearchTerm} 
                    globalDateRange={globalDateRange} 
                  />
                } 
              />
              {/* Add other routes as needed */}
            </Routes>
          </Container>
        </Box>
      </Flex>
    </Router>
  );
}

export default App;
