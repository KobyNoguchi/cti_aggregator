import React from "react";
import { BrowserRouter as Router, Routes, Route } from "react-router-dom";
import { Box, Flex, Heading, Container, SimpleGrid, GridItem } from "@chakra-ui/react";
import Dashboard from "./components/Dashboard";
import VulnerabilityTable from "./components/VulnerabilityTable";
import VulnerabilityPanel from './components/VulnerabilityPanel';
import IntelligenceFeed from './components/IntelligenceFeed';
import CrowdStrikeIntelPanel from './components/CrowdStrikeIntelPanel';
import MalwareFamiliesPanel from './components/MalwareFamiliesPanel';
import "./App.css";

function App() {
  const bgColor = "gray.50";
  const headerBgColor = "brand.500";
  const headerColor = "white";

  return (
    <Router>
      <Flex direction="column" minH="100vh" bg={bgColor}>
        {/* Banner */}
        <Box 
          as="header" 
          bg={headerBgColor} 
          color={headerColor} 
          py={4} 
          px={6} 
          boxShadow="md"
        >
          <Container maxW="container.xl">
            <Heading size="lg">CTI Aggregator</Heading>
          </Container>
        </Box>
        
        {/* Main Content */}
        <Box flex="1" p={4}>
          <Container maxW="container.xl" h="100%">
            <Routes>
              <Route path="/" element={<Dashboard />} />
              <Route path="/legacy" element={<VulnerabilityTable />} />
              {/* Add other routes as needed */}
            </Routes>
          </Container>
        </Box>
      </Flex>
    </Router>
  );
}

export default App;
