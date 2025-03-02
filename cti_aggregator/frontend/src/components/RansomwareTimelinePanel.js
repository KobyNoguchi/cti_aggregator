import React, { useEffect, useRef, useState } from 'react';
import { Box, Heading, Text, Input, Button, VStack, HStack, Spinner, useToast, ButtonGroup } from '@chakra-ui/react';
import * as d3 from 'd3';
import { read, utils } from 'xlsx';
import './RansomwareTimelinePanel.css';
import axios from 'axios';
import useDataFilters from '../utils/useDataFilters';

const RansomwareTimelinePanel = ({ searchTerm = '', dateRange = [null, null] }) => {
  const [rawData, setRawData] = useState([]);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState(null);
  const svgRef = useRef(null);
  const fileInputRef = useRef(null);
  const toast = useToast();
  
  // Use our custom filtering hook
  const { 
    filteredData: data, 
    handleSearch, 
    handleDateChange,
    hasActiveFilters
  } = useDataFilters(rawData, { 
    searchFields: ['organization', 'tools'], 
    dateField: 'date' 
  });
  
  // Sync with global filters when they change
  useEffect(() => {
    if (searchTerm) handleSearch(searchTerm);
    if (dateRange && dateRange[0] && dateRange[1]) handleDateChange(dateRange);
  }, [searchTerm, dateRange]);

  // Load CIRA data automatically when component mounts
  useEffect(() => {
    loadCiraData();
  }, []);

  const loadCiraData = async () => {
    setIsLoading(true);
    setError(null);

    try {
      let excelData;
      
      // First try to get the data from our backend API
      try {
        const response = await axios.get('/api/cira-data/', {
          responseType: 'arraybuffer'
        });
        excelData = response.data;
      } catch (apiError) {
        console.error("Error fetching from API, trying direct file access:", apiError);
        
        // If that fails, try to access the file directly (for development)
        const fallbackResponse = await axios.get('/data_sources/CIRA_Data.xlsx', {
          responseType: 'arraybuffer'
        });
        excelData = fallbackResponse.data;
      }
      
      const processedData = processExcelData(excelData);
      setRawData(processedData);
      
      toast({
        title: "CIRA data loaded successfully",
        description: `${processedData.length} ransomware attacks imported`,
        status: "success",
        duration: 5000,
        isClosable: true,
      });
    } catch (error) {
      console.error("Error loading CIRA data:", error);
      setError("Failed to load CIRA data. You can try uploading the file manually.");
      
      toast({
        title: "Error loading CIRA data",
        description: "Failed to load CIRA data automatically. You can try uploading the file manually.",
        status: "warning",
        duration: 5000,
        isClosable: true,
      });
    } finally {
      setIsLoading(false);
    }
  };

  const processExcelData = (excelData) => {
    try {
      const wb = read(excelData, { type: 'array' });
      const wsname = wb.SheetNames[0];
      const ws = wb.Sheets[wsname];
      const jsonData = utils.sheet_to_json(ws);
      
      // Validate and transform data
      if (jsonData.length === 0) {
        throw new Error("No data found in the spreadsheet");
      }
      
      // Try to determine the correct field names by inspecting the first row
      const firstRow = jsonData[0];
      const keys = Object.keys(firstRow);
      
      // Map fields based on likely column names
      const fieldMap = {
        date: keys.find(k => /date|time|when/i.test(k)) || keys[0],
        amount: keys.find(k => /amount|ransom|payment|paid|money/i.test(k)),
        tools: keys.find(k => /tool|malware|ransomware|software/i.test(k)),
        organization: keys.find(k => /org|company|victim|target/i.test(k))
      };
      
      console.log("Detected field mapping:", fieldMap);
      
      // Process dates to ensure they're in the right format and map fields
      const processedData = jsonData.map(item => {
        const mappedItem = {
          date: new Date(item[fieldMap.date]),
          amount: parseFloat(item[fieldMap.amount]) || 0,
          tools: item[fieldMap.tools] || "Unknown",
          organization: item[fieldMap.organization] || "Unknown"
        };
        
        // Validate the date
        if (isNaN(mappedItem.date.getTime())) {
          mappedItem.date = new Date(); // Fallback to current date if invalid
        }
        
        return mappedItem;
      }).sort((a, b) => a.date - b.date);
      
      return processedData;
    } catch (error) {
      console.error("Error processing Excel data:", error);
      throw error;
    }
  };

  const handleFileUpload = (event) => {
    const file = event.target.files[0];
    if (!file) return;

    setIsLoading(true);
    setError(null);

    const reader = new FileReader();
    reader.onload = (e) => {
      try {
        const processedData = processExcelData(e.target.result);
        setRawData(processedData);
        
        toast({
          title: "File loaded successfully",
          description: `${processedData.length} ransomware attacks imported`,
          status: "success",
          duration: 5000,
          isClosable: true,
        });
      } catch (error) {
        console.error("Error processing file:", error);
        setError(error.message);
        
        toast({
          title: "Error loading file",
          description: error.message,
          status: "error",
          duration: 5000,
          isClosable: true,
        });
      } finally {
        setIsLoading(false);
      }
    };
    
    reader.onerror = () => {
      setError("Failed to read the file");
      setIsLoading(false);
      
      toast({
        title: "Error",
        description: "Failed to read the file",
        status: "error",
        duration: 5000,
        isClosable: true,
      });
    };
    
    reader.readAsArrayBuffer(file);
  };

  const drawTimeline = (data) => {
    if (!data || data.length === 0 || !svgRef.current) return;

    // Clear previous visualization
    d3.select(svgRef.current).selectAll("*").remove();

    // Set dimensions and margins
    const margin = { top: 60, right: 30, bottom: 60, left: 60 };
    const width = 1000 - margin.left - margin.right;
    const height = 500 - margin.top - margin.bottom;

    // Create SVG element
    const svg = d3.select(svgRef.current)
      .attr("width", width + margin.left + margin.right)
      .attr("height", height + margin.top + margin.bottom)
      .append("g")
      .attr("transform", `translate(${margin.left},${margin.top})`);

    // Set up scales
    const xScale = d3.scaleTime()
      .domain(d3.extent(data, d => d.date))
      .range([0, width]);

    // Calculate max amount for y-scale
    const maxAmount = d3.max(data, d => d.amount) || 0;
    const yScale = d3.scaleLinear()
      .domain([0, maxAmount * 1.1]) // Add 10% padding at the top
      .range([height, 0]);

    // Add X axis
    svg.append("g")
      .attr("transform", `translate(0,${height})`)
      .call(d3.axisBottom(xScale))
      .selectAll("text")
      .style("text-anchor", "end")
      .attr("dx", "-.8em")
      .attr("dy", ".15em")
      .attr("transform", "rotate(-45)");

    // Add Y axis
    svg.append("g")
      .call(d3.axisLeft(yScale)
        .tickFormat(d => `$${d3.format(",.0f")(d)}`));

    // Create a color scale for tools
    const allTools = [...new Set(data.flatMap(d => d.tools ? d.tools.split(',').map(t => t.trim()) : []))];
    const colorScale = d3.scaleOrdinal()
      .domain(allTools)
      .range(d3.schemeCategory10);

    // Add dots
    svg.selectAll(".dot")
      .data(data)
      .enter()
      .append("circle")
      .attr("class", "dot")
      .attr("cx", d => xScale(d.date))
      .attr("cy", d => yScale(d.amount))
      .attr("r", 5)
      .style("fill", d => {
        // Use the first tool for color or default if no tools
        const firstTool = d.tools ? d.tools.split(',')[0].trim() : "Unknown";
        return colorScale(firstTool);
      })
      .style("opacity", 0.7)
      .style("stroke", "white")
      .on("mouseover", function(event, d) {
        d3.select(this)
          .transition()
          .duration(200)
          .attr("r", 10)
          .style("opacity", 1);
          
        // Create tooltip
        svg.append("text")
          .attr("class", "tooltip")
          .attr("x", xScale(d.date) + 10)
          .attr("y", yScale(d.amount) - 10)
          .style("font-size", "12px")
          .style("font-weight", "bold")
          .text(`${d.organization || 'Unknown'}: $${d3.format(",.0f")(d.amount)}`);
          
        svg.append("text")
          .attr("class", "tooltip")
          .attr("x", xScale(d.date) + 10)
          .attr("y", yScale(d.amount) + 5)
          .style("font-size", "10px")
          .text(`Date: ${d.date.toLocaleDateString()}`);
          
        svg.append("text")
          .attr("class", "tooltip")
          .attr("x", xScale(d.date) + 10)
          .attr("y", yScale(d.amount) + 20)
          .style("font-size", "10px")
          .text(`Tools: ${d.tools || 'Unknown'}`);
      })
      .on("mouseout", function() {
        d3.select(this)
          .transition()
          .duration(200)
          .attr("r", 5)
          .style("opacity", 0.7);
          
        // Remove tooltip
        svg.selectAll(".tooltip").remove();
      });

    // Add title
    svg.append("text")
      .attr("x", width / 2)
      .attr("y", -margin.top / 2)
      .attr("text-anchor", "middle")
      .style("font-size", "16px")
      .style("font-weight", "bold")
      .text("Ransomware Attacks Timeline");

    // Add X axis label
    svg.append("text")
      .attr("x", width / 2)
      .attr("y", height + margin.bottom - 10)
      .attr("text-anchor", "middle")
      .text("Date");

    // Add Y axis label
    svg.append("text")
      .attr("transform", "rotate(-90)")
      .attr("x", -height / 2)
      .attr("y", -margin.left + 15)
      .attr("text-anchor", "middle")
      .text("Ransom Amount ($)");

    // Add legend
    const legend = svg.append("g")
      .attr("class", "legend")
      .attr("transform", `translate(${width - 120}, 0)`);

    // Only display up to 10 tools in the legend to avoid overcrowding
    const displayTools = allTools.slice(0, 10);
    
    displayTools.forEach((tool, i) => {
      legend.append("circle")
        .attr("cx", 0)
        .attr("cy", i * 20)
        .attr("r", 5)
        .style("fill", colorScale(tool));
        
      legend.append("text")
        .attr("x", 10)
        .attr("y", i * 20 + 4)
        .style("font-size", "10px")
        .text(tool);
    });
    
    // Add "..." if there are more tools
    if (allTools.length > 10) {
      legend.append("text")
        .attr("x", 0)
        .attr("y", 10 * 20 + 4)
        .style("font-size", "10px")
        .text("+ " + (allTools.length - 10) + " more...");
    }
    
    // Add filter indicator if filters are active
    if (hasActiveFilters) {
      svg.append("text")
        .attr("x", width / 2)
        .attr("y", -margin.top / 2 + 20)
        .attr("text-anchor", "middle")
        .style("font-size", "12px")
        .style("fill", "red")
        .text("Filters Active - Showing filtered results");
    }
  };

  useEffect(() => {
    // If data is already available, draw the timeline
    drawTimeline(data);
  }, [data, hasActiveFilters]);

  const triggerFileUpload = () => {
    fileInputRef.current.click();
  };

  return (
    <Box className="ransomware-timeline-panel" p={4} borderRadius="md" boxShadow="md" bg="white">
      <VStack spacing={4} align="stretch">
        <Text>
          Visualizing CIRA ransomware attack data showing when attacks took place, 
          ransom amounts paid, and tools used by attackers.
        </Text>
        
        <HStack>
          <input
            type="file"
            ref={fileInputRef}
            onChange={handleFileUpload}
            accept=".xlsx,.xls"
            style={{ display: 'none' }}
          />
          <ButtonGroup>
            <Button onClick={loadCiraData} colorScheme="blue">
              Reload CIRA Data
            </Button>
            <Button onClick={triggerFileUpload} variant="outline">
              Upload Custom File
            </Button>
          </ButtonGroup>
        </HStack>
        
        {isLoading && (
          <Box textAlign="center" py={4}>
            <Spinner size="xl" />
            <Text mt={2}>Processing data...</Text>
          </Box>
        )}
        
        {error && (
          <Box bg="red.100" p={3} borderRadius="md">
            <Text color="red.800">{error}</Text>
          </Box>
        )}
        
        <Box className="timeline-container" overflow="auto" p={2}>
          <svg ref={svgRef}></svg>
        </Box>
        
        {data.length > 0 && (
          <Text fontSize="sm" color="gray.500">
            Showing {data.length} ransomware attacks 
            {data.length < rawData.length && ` (filtered from ${rawData.length} total)`}
            {data.length > 0 && ` from ${data[0].date.toLocaleDateString()} to ${data[data.length - 1].date.toLocaleDateString()}`}
          </Text>
        )}
      </VStack>
    </Box>
  );
};

export default RansomwareTimelinePanel; 