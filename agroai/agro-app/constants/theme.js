/**
 * AgroAI Design System - Theme Constants
 * Central source for colors, typography, spacing, and component styles
 */

export const COLORS = {
  background: '#0F172A',        // Deep navy - main background
  surface: '#1E293B',           // Slightly lighter - card background
  surfaceLight: '#293548',      // Elevated cards, input backgrounds
  accent: '#22C55E',            // Primary action green
  accentDim: '#16A34A',         // Pressed/active state
  accentGlow: 'rgba(34,197,94,0.15)',  // Glow background
  warning: '#F59E0B',           // Amber for warnings/alerts
  error: '#EF4444',             // Red for errors
  textPrimary: '#F1F5F9',       // Headings, primary text
  textSecondary: '#94A3B8',     // Subtext, secondary information
  textMuted: '#475569',         // Placeholders, disabled text
  border: '#334155',            // Card borders, dividers
  success: '#22C55E',           // Success indicator (same as accent)
  white: '#FFFFFF',             // Pure white
};

export const FONTS = {
  regular: 'System',
  medium: 'System',
  bold: 'System',
  sizes: {
    xs: 11,
    sm: 13,
    md: 15,
    lg: 17,
    xl: 20,
    xxl: 26,
    display: 34,
  },
};

export const SPACING = {
  xs: 4,
  sm: 8,
  md: 12,
  lg: 16,
  xl: 24,
  xxl: 32,
  xxxl: 48,
};

export const RADIUS = {
  sm: 8,
  md: 12,
  lg: 16,
  xl: 20,
  full: 999,
};

export const SHADOWS = {
  card: {
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 4 },
    shadowOpacity: 0.3,
    shadowRadius: 8,
    elevation: 8,
  },
};

export const CROP_ICONS = {
  Rice: '🌾',
  Wheat: '🌿',
  Maize: '🌽',
  Cotton: '🌸',
  Coffee: '☕',
  Tea: '🍵',
  Banana: '🍌',
  Mango: '🥭',
  Apple: '🍎',
  Orange: '🍊',
  Grapes: '🍇',
  Watermelon: '🍉',
  Coconut: '🥥',
  Papaya: '🫐',
  Jute: '🌱',
  default: '🌾',
};
