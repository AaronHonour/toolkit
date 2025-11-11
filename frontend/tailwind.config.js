/** @type {import('tailwindcss').Config} */
export default {
  content: [
    './packages/*/src/**/*.{js,ts,jsx,tsx}',
    '../examples/frontends/*/src/**/*.{js,ts,jsx,tsx}',
    '../examples/frontends/*/index.html',
  ],
  theme: {
    extend: {},
  },
  plugins: [],
};
