import { GameTheme } from '../types';

export const cockpitTheme: GameTheme = {
  name: 'cockpit',
  displayName: 'Spaceship Cockpit',
  description: 'Immersive spaceship command interface with HUD elements',
  
  colors: {
    // Primary - Electric blue for main HUD elements
    primary: '#00D9FF',
    primaryHover: '#00B8E6',
    primaryLight: '#33E1FF',
    primaryDark: '#0099CC',
    
    // Secondary - Orange/amber for warnings and highlights
    secondary: '#FF8C00',
    secondaryHover: '#FF7700',
    
    // Backgrounds - Deep space theme
    background: '#0A0A0F',
    backgroundSecondary: '#111116',
    surface: '#1A1A22',
    surfaceHover: '#252530',
    
    // Text - Light blue-white
    text: '#E0F6FF',
    textSecondary: '#B8DCF0',
    textMuted: '#7A8B99',
    
    // Status colors
    success: '#00FF7F',
    warning: '#FF8C00',
    error: '#FF4444',
    info: '#00D9FF',
    
    // UI elements
    border: '#334455',
    borderHover: '#00D9FF',
    shadow: 'rgba(0, 217, 255, 0.3)',
    overlay: 'rgba(10, 10, 15, 0.9)',
    
    // Game-specific
    credits: '#FFD700',
    turns: '#00FF7F',
    hazard: '#FF4444',
    radiation: '#FF6B35',
    energy: '#00D9FF',
  },
  
  fonts: {
    primary: '"Orbitron", "Exo 2", monospace',
    secondary: '"Roboto Condensed", sans-serif',
    monospace: '"JetBrains Mono", "Fira Code", monospace',
    heading: '"Orbitron", "Exo 2", monospace',
  },
  
  spacing: {
    xs: '0.25rem',   // 4px
    sm: '0.5rem',    // 8px
    md: '1rem',      // 16px
    lg: '1.5rem',    // 24px
    xl: '2rem',      // 32px
    '2xl': '3rem',   // 48px
    '3xl': '4rem',   // 64px
  },
  
  breakpoints: {
    mobile: '390px',    // iPhone 12/13/14 Pro width
    tablet: '768px',    // iPad Mini width
    desktop: '1024px',  // Desktop
    widescreen: '1440px', // Widescreen desktop
  },
  
  animations: {
    fast: '0.15s ease-out',
    normal: '0.3s ease-out',
    slow: '0.6s ease-out',
    pulse: '2s ease-in-out infinite',
    glow: '1.5s ease-in-out infinite alternate',
    scan: '3s linear infinite',
  },
  
  cssVariables: {
    // Colors
    '--color-primary': '#00D9FF',
    '--color-primary-hover': '#00B8E6',
    '--color-primary-light': '#33E1FF',
    '--color-primary-dark': '#0099CC',
    '--color-secondary': '#FF8C00',
    '--color-secondary-hover': '#FF7700',
    '--color-background': '#0A0A0F',
    '--color-background-secondary': '#111116',
    '--color-surface': '#1A1A22',
    '--color-surface-hover': '#252530',
    '--color-text': '#E0F6FF',
    '--color-text-secondary': '#B8DCF0',
    '--color-text-muted': '#7A8B99',
    '--color-success': '#00FF7F',
    '--color-warning': '#FF8C00',
    '--color-error': '#FF4444',
    '--color-info': '#00D9FF',
    '--color-border': '#334455',
    '--color-border-hover': '#00D9FF',
    '--color-shadow': 'rgba(0, 217, 255, 0.3)',
    '--color-overlay': 'rgba(10, 10, 15, 0.9)',
    '--color-credits': '#FFD700',
    '--color-turns': '#00FF7F',
    '--color-hazard': '#FF4444',
    '--color-radiation': '#FF6B35',
    '--color-energy': '#00D9FF',
    
    // Fonts
    '--font-primary': '"Orbitron", "Exo 2", monospace',
    '--font-secondary': '"Roboto Condensed", sans-serif',
    '--font-monospace': '"JetBrains Mono", "Fira Code", monospace',
    '--font-heading': '"Orbitron", "Exo 2", monospace',
    
    // Spacing
    '--space-xs': '0.25rem',
    '--space-sm': '0.5rem',
    '--space-md': '1rem',
    '--space-lg': '1.5rem',
    '--space-xl': '2rem',
    '--space-2xl': '3rem',
    '--space-3xl': '4rem',
    
    // Animations
    '--transition-fast': '0.15s ease-out',
    '--transition-normal': '0.3s ease-out',
    '--transition-slow': '0.6s ease-out',
    
    // Effects
    '--glow-primary': '0 0 20px rgba(0, 217, 255, 0.5)',
    '--glow-secondary': '0 0 20px rgba(255, 140, 0, 0.5)',
    '--glow-success': '0 0 20px rgba(0, 255, 127, 0.5)',
    '--glow-error': '0 0 20px rgba(255, 68, 68, 0.5)',
    
    // Borders
    '--border-radius': '6px',
    '--border-radius-lg': '12px',
    '--border-width': '1px',
    '--border-width-thick': '2px',
    
    // Shadows
    '--shadow-sm': '0 2px 4px rgba(0, 0, 0, 0.3)',
    '--shadow-md': '0 4px 12px rgba(0, 0, 0, 0.4)',
    '--shadow-lg': '0 8px 24px rgba(0, 0, 0, 0.5)',
    '--shadow-glow': '0 0 20px var(--color-shadow)',
  }
};