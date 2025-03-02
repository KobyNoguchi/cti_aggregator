import React, { useState } from 'react';
import {
  Box,
  Button,
  Flex,
  Input,
  Stack,
  Text
} from '@chakra-ui/react';

/**
 * A simple date range picker that doesn't rely on external datepicker libraries
 * to avoid the "Invalid hook call" error
 */
const SimpleDateRangePicker = ({ selectedDates = [new Date(), new Date()], onDateChange }) => {
  const [startDate, setStartDate] = useState(selectedDates[0] ? formatDateForInput(selectedDates[0]) : '');
  const [endDate, setEndDate] = useState(selectedDates[1] ? formatDateForInput(selectedDates[1]) : '');

  // Helper to format Date object to YYYY-MM-DD for input
  function formatDateForInput(date) {
    if (!date) return '';
    const d = new Date(date);
    let month = '' + (d.getMonth() + 1);
    let day = '' + d.getDate();
    const year = d.getFullYear();

    if (month.length < 2) month = '0' + month;
    if (day.length < 2) day = '0' + day;

    return [year, month, day].join('-');
  }

  // Handle start date change
  const handleStartDateChange = (e) => {
    const value = e.target.value;
    setStartDate(value);
    
    if (value && onDateChange) {
      onDateChange([new Date(value), endDate ? new Date(endDate) : new Date()]);
    }
  };

  // Handle end date change
  const handleEndDateChange = (e) => {
    const value = e.target.value;
    setEndDate(value);
    
    if (value && onDateChange) {
      onDateChange([startDate ? new Date(startDate) : new Date(), new Date(value)]);
    }
  };

  // Clear the date selection
  const handleClear = () => {
    setStartDate('');
    setEndDate('');
    
    if (onDateChange) {
      onDateChange([null, null]);
    }
  };

  return (
    <Box width="100%">
      <Stack spacing={3}>
        <Box>
          <Text fontSize="sm" mb={1}>Start Date</Text>
          <Input
            type="date"
            value={startDate}
            onChange={handleStartDateChange}
            size="sm"
          />
        </Box>
        
        <Box>
          <Text fontSize="sm" mb={1}>End Date</Text>
          <Input
            type="date"
            value={endDate}
            onChange={handleEndDateChange}
            size="sm"
          />
        </Box>
        
        <Flex justify="flex-end">
          <Button size="sm" variant="ghost" onClick={handleClear}>
            Clear
          </Button>
        </Flex>
      </Stack>
    </Box>
  );
};

export default SimpleDateRangePicker; 