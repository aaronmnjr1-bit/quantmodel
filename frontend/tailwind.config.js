/** @type {import('tailwindcss').Config} */
export default {
  darkMode: 'class',
  content: [
    './index.html',
    './src/**/*.{js,ts,jsx,tsx}',
  ],
  theme: {
    extend: {
      colors: {
        terminal: {
          bg: '#0a0a0a',
          surface: '#111111',
          border: '#1e1e1e',
          text: '#e0e0e0',
          muted: '#6b7280',
          green: '#00c853',
          red: '#ff1744',
          amber: '#ffab00',
          blue: '#2979ff',
          cyan: '#00e5ff',
        },
      },
      fontFamily: {
        mono: ['JetBrains Mono', 'Fira Code', 'Consolas', 'monospace'],
        sans: ['Inter', 'system-ui', 'sans-serif'],
      },
    },
  },
  plugins: [],
}
