import {heroui} from "@heroui/theme"

/** @type {import('tailwindcss').Config} */
module.exports = {
  content: [
    './components/**/*.{js,ts,jsx,tsx,mdx}',
    './app/**/*.{js,ts,jsx,tsx,mdx}',
    "./node_modules/@heroui/theme/dist/**/*.{js,ts,jsx,tsx}"
  ],
  theme: {
    extend: {
      fontFamily: {
        sans: ["var(--font-sans)"],
        mono: ["var(--font-mono)"],
      },
      colors: {
        primary: {
          DEFAULT: '#006FEE',
          foreground: '#FFFFFF',
        },
        secondary: {
          DEFAULT: '#7828C8',
          foreground: '#FFFFFF',
        },
        success: {
          DEFAULT: '#17C964',
          foreground: '#FFFFFF',
        },
        warning: {
          DEFAULT: '#F5A524',
          foreground: '#FFFFFF',
        },
        danger: {
          DEFAULT: '#F31260',
          foreground: '#FFFFFF',
        },
      },
    },
  },
  darkMode: "class",
  plugins: [heroui()],
}
