/** @type {import('tailwindcss').Config} */
export default {
  content: ['./index.html', './src/**/*.{js,ts,jsx,tsx}'],
  theme: {
    extend: {
      colors: {
        // Sistema de colores Agri-Scientific Precision (Stitch)
        primary: '#00346f',
        'primary-container': '#004a99',
        'on-primary': '#ffffff',
        'on-primary-container': '#9bbdff',
        secondary: '#b6171e',
        'secondary-container': '#da3433',
        'on-secondary': '#ffffff',
        tertiary: '#003f0b',
        'tertiary-container': '#005914',
        'on-tertiary-container': '#7ecf79',
        surface: '#f8f9fa',
        'surface-dim': '#d9dadb',
        'surface-bright': '#f8f9fa',
        'surface-container-lowest': '#ffffff',
        'surface-container-low': '#f3f4f5',
        'surface-container': '#edeeef',
        'surface-container-high': '#e7e8e9',
        'surface-container-highest': '#e1e3e4',
        'on-surface': '#191c1d',
        'on-surface-variant': '#424751',
        outline: '#737783',
        'outline-variant': '#c2c6d3',
        error: '#ba1a1a',
        'error-container': '#ffdad6',
        'on-error-container': '#93000a',
        background: '#f8f9fa',
      },
      fontFamily: {
        display: ['Space Grotesk', 'system-ui', 'sans-serif'],
        body: ['Public Sans', 'system-ui', 'sans-serif'],
        mono: ['Space Grotesk', 'system-ui', 'sans-serif'],
      },
      borderRadius: {
        DEFAULT: '0.25rem',
        sm: '0.125rem',
        md: '0.375rem',
        lg: '0.5rem',
        xl: '0.75rem',
        full: '9999px',
      },
      boxShadow: {
        card: '0 1px 3px 0 rgba(0,0,0,0.08)',
        'card-hover': '0 4px 12px 0 rgba(0,0,0,0.12)',
      },
      maxWidth: {
        container: '1280px',
      },
    },
  },
  plugins: [],
}
