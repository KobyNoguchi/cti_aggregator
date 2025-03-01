import React from 'react';
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

const Dashboard = () => {
  const panelBg = 'white';
  const headerBg = 'blue.500';
  const headerColor = 'white';
  const csHeaderBg = 'red.500';

  return (
    <Box h="full">
      <Grid
        templateColumns={{ base: '1fr', md: 'repeat(4, 1fr)' }}
        templateRows={{ base: 'repeat(6, 1fr)', md: 'repeat(5, 1fr)' }}
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
          overflow="auto"
          height={{ base: "auto", md: "400px" }}
        >
          <Flex p={4} bg={headerBg} justify="space-between" align="center">
            <Heading as="h3" size="md">Threat Intelligence</Heading>
          </Flex>
          <Box p={4}>
            <IntelligenceFeed />
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
          overflow="auto"
          height={{ base: "auto", md: "400px" }}
        >
          <Box p={4}>
            <MalwareFamiliesPanel />
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
          overflow="auto"
          height={{ base: "auto", md: "400px" }}
        >
          <Flex p={4} bg={headerBg} justify="space-between" align="center">
            <Heading as="h3" size="md">CrowdStrike Threat Intelligence</Heading>
          </Flex>
          <Box p={4}>
            <CrowdStrikeIntelPanel />
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
          overflow="auto"
          height={{ base: "auto", md: "400px" }}
        >
          <Flex p={4} bg={headerBg} justify="space-between" align="center">
            <Heading as="h3" size="md">CISA Known Exploited Vulnerabilities</Heading>
          </Flex>
          <Box p={4}>
            <VulnerabilityPanel dataSource="cisa" />
          </Box>
        </GridItem>

        {/* NVD Vulnerabilities Panel */}
        <GridItem 
          colSpan={{ base: 1, md: 4 }} 
          rowSpan={{ base: 1, md: 1 }}
          gridRow={{ base: 5, md: 4 }}
          bg={panelBg}
          borderRadius="md"
          boxShadow="sm"
          overflow="auto"
          height={{ base: "auto", md: "400px" }}
        >
          <Flex p={4} bg={headerBg} justify="space-between" align="center">
            <Heading as="h3" size="md">NVD Vulnerability Alerts</Heading>
          </Flex>
          <Box p={4}>
            <VulnerabilityPanel />
          </Box>
        </GridItem>
      </Grid>
    </Box>
  );
};

export default Dashboard;
