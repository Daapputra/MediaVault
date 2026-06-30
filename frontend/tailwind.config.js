/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        background: '#0f0f23',
        surface: '#1a1a3e',
        'surface-hover': '#252552',
        border: '#2d2d6b',
        primary: '#6c63ff',
        'primary-hover': '#5a52d9',
        secondary: '#00d4aa',
        success: '#22c55e',
        warning: '#f59e0b',
        error: '#ef4444',
        'text-primary': '#e2e8f0',
        'text-secondary': '#94a3b8',
      },
      fontFamily: {
        sans: ['Inter', 'sans-serif'],
      },
    },
  },
  plugins: [],
}
