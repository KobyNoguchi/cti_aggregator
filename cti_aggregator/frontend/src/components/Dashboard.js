import React, { useEffect } from 'react';
import { 
  Grid, 
  GridItem, 
  Box, 
  Heading,
  Flex
} from '@chakra-ui/react';
import VulnerabilityPanel from './VulnerabilityPanel';
import IntelligenceFeed from './IntelligenceFeed';
import CrowdStrikeIntelPanel from './CrowdStrikeIntelPanel';
import MalwareFamiliesPanel from './MalwareFamiliesPanel';
import RansomwareTimelinePanel from './RansomwareTimelinePanel';
import GlobalHeader from './common/GlobalHeader';

const Dashboard = ({ globalSearchTerm = '', globalDateRange = [null, null] }) => {
  const panelBg = 'white';
  const headerBg = 'blue.500';
  const headerColor = 'white';
  const csHeaderBg = 'red.500';

  // This effect syncs the global filters when they change
  useEffect(() => {
    // You could add additional global filter handling here
    console.log('Global filters changed:', { globalSearchTerm, globalDateRange });
  }, [globalSearchTerm, globalDateRange]);

  return (
    <Box h="full">
      <Grid
        templateColumns={{ base: '1fr', md: 'repeat(4, 1fr)' }}
        templateRows={{ base: 'repeat(7, 1fr)', md: 'repeat(6, 1fr)' }}
        gap={4}
        p={4}
      >
        {/* Threat Intelligence Panel */}
        <GridItem 
          colSpan={{ base: 1, md: 4 }} 
          rowSpan={{ base: 1, md: 1 }}
          bg={panelBg}
          borderRadius="md"
          boxShadow="sm"
          overflow="hidden" // Changed from auto to hidden to work with sticky header
          height={{ base: "auto", md: "400px" }}
        >
          <GlobalHeader 
            title="Threat Intelligence"
            bg={headerBg}
            color={headerColor}
            onSearch={(term) => console.log('Threat Intel search:', term)}
            onDateChange={(dates) => console.log('Threat Intel date change:', dates)}
          />
          <Box p={4} overflowY="auto" height="calc(100% - 51px)">
            <IntelligenceFeed 
              searchTerm={globalSearchTerm}
              dateRange={globalDateRange}
            />
          </Box>
        </GridItem>

        {/* CrowdStrike Malware Families Panel */}
        <GridItem 
          colSpan={{ base: 1, md: 4 }} 
          rowSpan={{ base: 1, md: 1 }}
          gridRow={{ base: 3, md: 2 }}
          gridColumn={{ base: 1, md: 1 }}
          bg={panelBg}
          borderRadius="md"
          boxShadow="sm"
          overflow="hidden"
          height={{ base: "auto", md: "400px" }}
        >
          <GlobalHeader 
            title="Malware Families"
            bg={headerBg}
            color={headerColor}
          />
          <Box p={4} overflowY="auto" height="calc(100% - 51px)">
            <MalwareFamiliesPanel 
              searchTerm={globalSearchTerm}
              dateRange={globalDateRange}
            />
          </Box>
        </GridItem>

        {/* CrowdStrike Intelligence Panel */}
        <GridItem 
          colSpan={{ base: 1, md: 2 }} 
          rowSpan={{ base: 1, md: 1 }}
          gridRow={{ base: 2, md: 3 }}
          gridColumn={{ base: 1, md: 1 }}
          bg={panelBg}
          borderRadius="md"
          boxShadow="sm"
          overflow="hidden"
          height={{ base: "auto", md: "400px" }}
        >
          <GlobalHeader 
            title="CrowdStrike Threat Intelligence"
            bg={headerBg}
            color={headerColor}
          />
          <Box p={4} overflowY="auto" height="calc(100% - 51px)">
            <CrowdStrikeIntelPanel 
              searchTerm={globalSearchTerm}
              dateRange={globalDateRange}
            />
          </Box>
        </GridItem>

        {/* CISA KEV Panel */}
        <GridItem 
          colSpan={{ base: 1, md: 2 }} 
          rowSpan={{ base: 1, md: 1 }}
          gridRow={{ base: 4, md: 3 }}
          gridColumn={{ base: 1, md: 3 }}
          bg={panelBg}
          borderRadius="md"
          boxShadow="sm"
          overflow="hidden"
          height={{ base: "auto", md: "400px" }}
        >
          <GlobalHeader 
            title="CISA Known Exploited Vulnerabilities"
            bg={headerBg}
            color={headerColor}
          />
          <Box p={4} overflowY="auto" height="calc(100% - 51px)">
            <VulnerabilityPanel 
              dataSource="cisa" 
              searchTerm={globalSearchTerm}
              dateRange={globalDateRange}
            />
          </Box>
        </GridItem>

        {/* Ransomware Timeline Panel */}
        <GridItem 
          colSpan={{ base: 1, md: 4 }} 
          rowSpan={{ base: 1, md: 1 }}
          gridRow={{ base: 6, md: 5 }}
          bg={panelBg}
          borderRadius="md"
          boxShadow="sm"
          overflow="hidden"
          height={{ base: "auto", md: "600px" }}
        >
          <GlobalHeader 
            title="Ransomware Attack Timeline"
            bg={headerBg}
            color={headerColor}
          />
          <Box p={4} overflowY="auto" height="calc(100% - 51px)">
            <RansomwareTimelinePanel 
              searchTerm={globalSearchTerm}
              dateRange={globalDateRange}
            />
          </Box>
        </GridItem>

        {/* NVD Vulnerabilities Panel - moved to row 6 */}
        <GridItem 
          colSpan={{ base: 1, md: 4 }} 
          rowSpan={{ base: 1, md: 1 }}
          gridRow={{ base: 7, md: 6 }}
          bg={panelBg}
          borderRadius="md"
          boxShadow="sm"
          overflow="hidden"
          height={{ base: "auto", md: "400px" }}
        >
          <GlobalHeader 
            title="NVD Vulnerability Alerts"
            bg={headerBg}
            color={headerColor}
          />
          <Box p={4} overflowY="auto" height="calc(100% - 51px)">
            <VulnerabilityPanel 
              searchTerm={globalSearchTerm}
              dateRange={globalDateRange}
            />
          </Box>
        </GridItem>
      </Grid>
    </Box>
  );
};

export default Dashboard;
