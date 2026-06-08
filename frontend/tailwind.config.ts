import type { Config } from 'tailwindcss';

const config: Config = {
  darkMode: 'class',
  content: [
    './app/**/*.{ts,tsx}',
    './components/**/*.{ts,tsx}',
  ],
  theme: {
    extend: {
      colors: {
        primary: {
          50:  'hsl(222, 47%, 96%)',
          100: 'hsl(222, 47%, 91%)',
          200: 'hsl(222, 47%, 82%)',
          300: 'hsl(222, 47%, 70%)',
          400: 'hsl(222, 47%, 58%)',
          500: 'hsl(222, 47%, 46%)',
          600: 'hsl(222, 47%, 38%)',
          700: 'hsl(222, 47%, 30%)',
          800: 'hsl(222, 47%, 22%)',
          900: 'hsl(222, 47%, 15%)',
          950: 'hsl(222, 47%, 9%)',
        },
        accent: {
          50:  'hsl(199, 89%, 96%)',
          100: 'hsl(199, 89%, 89%)',
          200: 'hsl(199, 89%, 78%)',
          300: 'hsl(199, 89%, 65%)',
          400: 'hsl(199, 89%, 52%)',
          500: 'hsl(199, 89%, 42%)',
          600: 'hsl(205, 85%, 35%)',
          700: 'hsl(210, 80%, 28%)',
          800: 'hsl(215, 75%, 20%)',
          900: 'hsl(220, 70%, 14%)',
          950: 'hsl(225, 65%, 8%)',
        },
        surface: {
          DEFAULT: '#0f1117',
          elevated: '#1a1d27',
          card: '#20243a',
        },
        border: {
          subtle: '#2a2d3e',
          default: '#383b52',
        },
        text: {
          primary: '#e8eaf0',
          secondary: '#9ba3c0',
          muted: '#5c6384',
        },
        success: '#22c55e',
        warning: '#f59e0b',
        error: '#ef4444',
        info: '#3b82f6',
      },
      fontFamily: {
        sans: ['Inter', 'system-ui', 'sans-serif'],
      },
      animation: {
        'fade-in': 'fadeIn 0.2s ease-in',
        'slide-up': 'slideUp 0.3s ease-out',
        'pulse-dot': 'pulseDot 2s infinite',
        'slide-in-right': 'slideInRight 0.3s ease-out',
        'spin-slow': 'spin 1.5s linear infinite',
      },
      keyframes: {
        fadeIn: {
          '0%':   { opacity: '0' },
          '100%': { opacity: '1' },
        },
        slideUp: {
          '0%':   { opacity: '0', transform: 'translateY(12px)' },
          '100%': { opacity: '1', transform: 'translateY(0)' },
        },
        pulseDot: {
          '0%, 100%': { transform: 'scale(1)',   opacity: '1' },
          '50%':       { transform: 'scale(1.4)', opacity: '0.7' },
        },
        slideInRight: {
          '0%':   { opacity: '0', transform: 'translateX(100%)' },
          '100%': { opacity: '1', transform: 'translateX(0)' },
        },
      },
      backdropBlur: {
        xs: '2px',
      },
      boxShadow: {
        'glass': '0 8px 32px rgba(0, 0, 0, 0.4), inset 0 1px 0 rgba(255,255,255,0.05)',
        'card':  '0 4px 24px rgba(0, 0, 0, 0.3)',
        'glow-accent': '0 0 20px rgba(14, 165, 233, 0.25)',
      },
    },
  },
  plugins: [],
};

export default config;
