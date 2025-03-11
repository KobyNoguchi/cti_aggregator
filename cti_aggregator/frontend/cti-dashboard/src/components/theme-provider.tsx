"use client";

import * as React from "react";
import { ThemeProvider as NextThemesProvider } from "next-themes";

type Attribute = 'class' | 'data-theme' | 'data-mode';

export interface ThemeProviderProps {
  children: React.ReactNode;
  defaultTheme?: string;
  attribute?: Attribute;
  enableSystem?: boolean;
  [key: string]: any;
}

export function ThemeProvider({ 
  children, 
  defaultTheme = "dark",
  attribute = "class",
  enableSystem = false,
  ...props 
}: ThemeProviderProps) {
  return (
    <NextThemesProvider 
      {...props} 
      attribute={attribute} 
      defaultTheme={defaultTheme} 
      enableSystem={enableSystem}
    >
      {children}
    </NextThemesProvider>
  );
} 