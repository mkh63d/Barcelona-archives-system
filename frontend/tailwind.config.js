/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{vue,js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        primary: {
          DEFAULT: '#009639',
          50: '#00ff5c',
          100: '#00eb55',
          200: '#00d14c',
          300: '#00b742',
          400: '#009639',
          500: '#007c30',
          600: '#006226',
          700: '#00481d',
          800: '#002e13',
          900: '#00140a',
        },
        dark: {
          DEFAULT: '#1a1a1a',
          50: '#4a4a4a',
          100: '#3a3a3a',
          200: '#2a2a2a',
          300: '#1a1a1a',
          400: '#151515',
          500: '#0f0f0f',
          600: '#0a0a0a',
          700: '#050505',
          800: '#000000',
          900: '#000000',
        }
      },
    },
  },
  plugins: [],
}
