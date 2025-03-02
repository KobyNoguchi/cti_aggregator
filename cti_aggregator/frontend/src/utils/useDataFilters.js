import { useState, useEffect, useMemo } from 'react';

/**
 * Custom hook for filtering data based on search term and date range
 * @param {Array} data - The array of data objects to filter
 * @param {Object} options - Configuration options
 * @param {string} options.searchFields - Array of field names to search within
 * @param {string} options.dateField - The field name containing date information
 * @returns {Object} - The filtered data and filter state
 */
const useDataFilters = (data = [], { searchFields = [], dateField = 'date' } = {}) => {
  const [searchTerm, setSearchTerm] = useState('');
  const [dateRange, setDateRange] = useState([null, null]);
  
  // Function to handle search
  const handleSearch = (term) => {
    setSearchTerm(term);
  };
  
  // Function to handle date range changes
  const handleDateChange = (dates) => {
    setDateRange(dates);
  };
  
  // Apply filters to data
  const filteredData = useMemo(() => {
    if (!data.length) return [];
    
    return data.filter(item => {
      // Search filter
      const matchesSearch = !searchTerm || searchFields.some(field => {
        const fieldValue = String(item[field] || '').toLowerCase();
        return fieldValue.includes(searchTerm.toLowerCase());
      });
      
      // Date range filter
      const [startDate, endDate] = dateRange;
      const itemDate = item[dateField] instanceof Date 
        ? item[dateField] 
        : new Date(item[dateField]);
      
      const withinDateRange = 
        !startDate || !endDate || 
        (itemDate >= startDate && itemDate <= endDate);
      
      return matchesSearch && withinDateRange;
    });
  }, [data, searchTerm, dateRange, searchFields, dateField]);
  
  return {
    filteredData,
    searchTerm,
    dateRange,
    handleSearch,
    handleDateChange,
    hasActiveFilters: searchTerm !== '' || (dateRange[0] !== null && dateRange[1] !== null)
  };
};

export default useDataFilters; 