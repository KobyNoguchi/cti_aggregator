# Dark Mode Implementation

This implementation adds a dark mode toggle to the CTI Dashboard with dark mode as the default.

## Installation

Before running the application, you need to install the `next-themes` package:

```bash
# Navigate to the project directory
cd cti_aggregator/frontend/cti-dashboard

# Install next-themes
npm install next-themes
```

## Implementation Details

The dark mode implementation consists of the following components:

1. **ThemeProvider** (`src/components/theme-provider.tsx`): Wraps the application to provide theme context.
2. **ThemeToggle** (`src/components/theme-toggle.tsx`): A toggle button that switches between light and dark modes.
3. **Layout update** (`src/app/layout.tsx`): Updated to include the theme provider and toggle button.
4. **CSS variables** (`src/app/globals.css`): Already has dark mode color variables defined.

## Features

- Dark mode is set as the default theme
- Soft black color scheme similar to Cursor's default theme
- Theme preference is saved to localStorage
- Smooth transitions between light and dark modes

## Usage

Click the sun/moon icon in the header to toggle between light and dark mode.

## How it Works

The implementation uses the `next-themes` package to manage theme switching. The ThemeProvider component wraps the application and provides theme context to all components. The ThemeToggle component uses the `useTheme` hook from `next-themes` to toggle between light and dark modes.

When in dark mode, the `dark` class is added to the `html` element, which triggers the CSS variables defined in `globals.css` to use the dark mode color values. 