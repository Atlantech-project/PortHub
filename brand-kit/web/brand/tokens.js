// ATLANTECH design tokens for JavaScript (charts, canvas, inline styles).
// For styling, prefer the CSS variables in css/tokens.css; they follow light/dark.

export const palette = Object.freeze({
  deepNavy: '#083A4F',
  mutedGold: '#A58D66',
  lightTeal: '#C0D5D6',
  midTeal: '#407E8C',
  offWhite: '#E5E1DD',
});

export const light = Object.freeze({
  bg: '#F7F5F2',
  surface: '#FFFFFF',
  text: '#0F2A36',
  textMuted: '#4B5F68',
  border: '#D3DEDF',
  primary: '#083A4F',
  onPrimary: '#E5E1DD',
  accent: '#A58D66',
  accentText: '#7A6440',
  link: '#407E8C',
  success: '#2E7D5B',
  warning: '#8A5C0F',
  danger: '#B3412F',
});

export const dark = Object.freeze({
  bg: '#04222F',
  surface: '#072B3A',
  text: '#E5E1DD',
  textMuted: '#A9BEC3',
  border: '#1E4A5B',
  primary: '#C0D5D6',
  onPrimary: '#083A4F',
  accent: '#C2A77B',
  accentText: '#C2A77B',
  link: '#7FB4BF',
  success: '#7CC9A4',
  warning: '#E3B766',
  danger: '#F2A493',
});

// Series order for charts: navy, teal, gold, light teal, then their dark-mode lifts.
export const chartSeries = Object.freeze(['#083A4F', '#407E8C', '#A58D66', '#8FB8BF', '#5B4A30']);

export const fonts = Object.freeze({
  display: '"Montserrat", ui-sans-serif, system-ui, sans-serif',
  body: '"Inter", ui-sans-serif, system-ui, sans-serif',
});

export default { palette, light, dark, chartSeries, fonts };
