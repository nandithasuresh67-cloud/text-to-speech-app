/** @type {import('tailwindcss').Config} */
export default {
  content: [
    './index.html',
    './src/**/*.{js,jsx}',
  ],
  theme: {
    extend: {
      colors: {
        brand: {
          50: '#f2f5ff',
          100: '#e6ecff',
          500: '#4f5fe0',
          600: '#3f4dc9',
          700: '#333fa3',
        },
      },
    },
  },
  plugins: [],
}
