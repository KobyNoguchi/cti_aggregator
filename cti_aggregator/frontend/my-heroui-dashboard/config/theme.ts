// Define custom colors for the dark theme
export const customColors = {
  // Base colors
  background: {
    light: "#FFFFFF",
    dark: "#121212", // Darker background
  },
  foreground: {
    light: "#11181C",
    dark: "#ECEDEE", // Light text for dark mode
  },
  
  // Primary colors - can be adjusted to your preference
  primary: {
    light: "#006FEE",
    dark: "#3694FF", // Brighter blue for dark mode
  },
  
  // Secondary colors
  secondary: {
    light: "#7828C8",
    dark: "#9750DD", // Brighter purple for dark mode
  },
  
  // Success colors
  success: {
    light: "#17C964",
    dark: "#21E980", // Brighter green for dark mode
  },
  
  // Warning colors
  warning: {
    light: "#F5A524",
    dark: "#FFC73A", // Brighter yellow for dark mode
  },
  
  // Danger colors
  danger: {
    light: "#F31260",
    dark: "#FF4D82", // Brighter red for dark mode
  },
  
  // Focus color
  focus: {
    light: "#006FEE",
    dark: "#3694FF", // Brighter blue for dark mode
  },
};

// Create a custom theme config
export const customTheme = {
  extend: {
    colors: {
      // Add your custom colors here if needed
    },
  },
  theme: {
    colors: customColors,
  }
}; 