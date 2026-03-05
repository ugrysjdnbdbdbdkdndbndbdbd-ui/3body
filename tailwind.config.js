/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{vue,js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        // The Void Canvas
        void: {
          deep: '#000510', // Deepest cold navy black
          DEFAULT: '#020817',
          light: '#0A1025',
        },
        // The Light of Physics
        sophon: {
          dim: 'rgba(0, 255, 200, 0.1)',
          DEFAULT: '#00FFC8', // Colder, ethereal cyan-green
          bright: '#E0FFF8',
        },
        // Entropy / Warning
        collapse: {
          DEFAULT: '#FF3C00', // Red giant star
          dim: 'rgba(255, 60, 0, 0.2)',
        }
      },
      fontFamily: {
        sans: ['Inter', 'ui-sans-serif', 'system-ui', 'sans-serif'],
        mono: ['"JetBrains Mono"', '"Space Mono"', 'ui-monospace', 'monospace'],
        // For the massive headers
        display: ['Inter', 'sans-serif'], 
      },
      fontSize: {
        // Monolithic scales for "Architecture"
        'monolith': ['8rem', { lineHeight: '1', letterSpacing: '-0.02em', fontWeight: '100' }],
        'macro': ['4rem', { lineHeight: '1.1', letterSpacing: '0.1em', fontWeight: '200' }],
      },
      letterSpacing: {
        'cosmic': '0.3em', // For subtitles floating in void
      },
      boxShadow: {
        'sophon-glow': '0 0 20px rgba(0, 255, 200, 0.15)',
        'collapse-glow': '0 0 20px rgba(255, 60, 0, 0.15)',
      },
      animation: {
        'unfold': 'unfold 1.2s cubic-bezier(0.16, 1, 0.3, 1) forwards',
        'drift': 'drift 240s linear infinite',
        'breath': 'breath 12s ease-in-out infinite',
      },
      keyframes: {
        unfold: {
          '0%': { opacity: '0', transform: 'scale(0.96) translateY(10px)' },
          '100%': { opacity: '1', transform: 'scale(1) translateY(0)' },
        },
        drift: {
          '0%': { backgroundPosition: '0% 0%' },
          '100%': { backgroundPosition: '100% 100%' },
        },
        breath: {
          '0%, 100%': { opacity: '0.4' },
          '50%': { opacity: '0.7' },
        }
      }
    },
  },
  plugins: [],
}
