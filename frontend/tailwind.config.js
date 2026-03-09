/** @type {import('tailwindcss').Config} */
export default {
  content: ["./index.html", "./src/**/*.{js,ts,jsx,tsx}"],
  theme: {
    extend: {
      colors: {
        airbnb: {
          DEFAULT: "#FF385C",
          dark: "#D70466",
          light: "#FF8FA3",
        },
        dark: "#222222",
        gray: {
          airbnb: "#717171",
        },
      },
      fontFamily: {
        sans: ['"Inter"', "system-ui", "-apple-system", "sans-serif"],
      },
    },
  },
  plugins: [],
};
