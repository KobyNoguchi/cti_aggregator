import React from 'react';
import { 
  Grid, 
  GridItem, 
  Box, 
  Heading
} from '@chakra-ui/react';
import VulnerabilityPanel from './VulnerabilityPanel';
import IntelligenceFeed from './IntelligenceFeed';
import CrowdStrikeIntelPanel from './CrowdStrikeIntelPanel';

const Dashboard = () => {
  const panelBg = 'white';
  const headerBg = 'blue.500';
  const headerColor = 'white';
  const csHeaderBg = 'red.500';

  return (
    <Box h="full">
      <Grid
        templateColumns={{ base: '1fr', md: 'repeat(4, 1fr)' }}
        templateRows={{ base: 'repeat(4, 1fr)', md: 'repeat(2, 1fr)' }}
        gap={4}
        h="full"
      >
        {/* Intelligence Feed Panel */}
        <GridItem 
          colSpan={{ base: 1, md: 1 }} 
          rowSpan={{ base: 1, md: 1 }}
          bg={panelBg}
          borderRadius="md"
          boxShadow="sm"
          overflow="hidden"
        >
          <Box 
            bg={headerBg} 
            color={headerColor} 
            p={3}
          >
            <Heading size="md">Intelligence Feed</Heading>
          </Box>
          <Box p={3} h="calc(100% - 50px)" overflow="hidden">
            <IntelligenceFeed />
          </Box>
        </GridItem>
        
        {/* CrowdStrike Threat Intelligence Panel */}
        <GridItem 
          colSpan={{ base: 1, md: 1 }} 
          rowSpan={{ base: 1, md: 1 }}
          bg={panelBg}
          borderRadius="md"
          boxShadow="sm"
          overflow="hidden"
        >
          <Box 
            bg={csHeaderBg} 
            color={headerColor} 
            p={3}
          >
            <Heading size="md">Threat Intelligence</Heading>
          </Box>
          <Box p={3} h="calc(100% - 50px)" overflow="hidden">
            <CrowdStrikeIntelPanel />
          </Box>
        </GridItem>
        
        {/* CISA KEV Panel */}
        <GridItem 
          colSpan={{ base: 1, md: 2 }} 
          rowSpan={{ base: 1, md: 2 }}
          bg={panelBg}
          borderRadius="md"
          boxShadow="sm"
          overflow="hidden"
        >
          <Box 
            bg={headerBg} 
            color={headerColor} 
            p={3}
          >
            <Heading size="md">CISA Known Exploited Vulnerabilities (KEV)</Heading>
          </Box>
          <Box p={3} h="calc(100% - 50px)" overflow="hidden">
            <VulnerabilityPanel dataSource="cisa" />
          </Box>
        </GridItem>
        
        {/* NVD Vulnerabilities Panel */}
        <GridItem 
          colSpan={{ base: 1, md: 1 }} 
          rowSpan={{ base: 1, md: 1 }}
          bg={panelBg}
          borderRadius="md"
          boxShadow="sm"
          overflow="hidden"
          display={{ base: "block", md: "block" }}
        >
          <Box 
            bg={headerBg} 
            color={headerColor} 
            p={3}
          >
            <Heading size="md">NVD Vulnerabilities</Heading>
          </Box>
          <Box p={3} h="calc(100% - 50px)" overflow="hidden">
            <p>NVD data will be displayed here</p>
          </Box>
        </GridItem>
      </Grid>
    </Box>
  );
};

export default Dashboard;
