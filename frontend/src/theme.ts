import { createTheme, responsiveFontSizes } from '@mui/material/styles';

/** Augments MUI palette with LogRoute brand and ELD duty-status colours. */
declare module '@mui/material/styles' {
  interface Palette {
    brand: {
      teal: string;
      amber: string;
    };
    eld?: {
      offDuty: string;
      sleeperBerth: string;
      driving: string;
      onDuty: string;
    };
  }
  interface PaletteOptions {
    brand?: {
      teal?: string;
      amber?: string;
    };
    eld?: {
      offDuty?: string;
      sleeperBerth?: string;
      driving?: string;
      onDuty?: string;
    };
  }
}

const baseTheme = createTheme({
  palette: {
    primary: {
      main: '#0D3B4E',
      light: '#1A5570',
      dark: '#082A38',
      contrastText: '#FFFFFF',
    },
    secondary: {
      main: '#F59E0B',
      light: '#FCD34D',
      dark: '#D97706',
      contrastText: '#0D3B4E',
    },
    background: {
      default: '#F8FAFC',
      paper: '#FFFFFF',
    },
    text: {
      primary: '#111827',
      secondary: '#4B5563',
    },
    success: { main: '#10B981' },
    error: { main: '#EF4444' },
    warning: { main: '#F59E0B' },
    divider: '#E2E8F0',
    brand: {
      teal: '#0D3B4E',
      amber: '#F59E0B',
    },
    eld: {
      offDuty: '#6B7280',
      sleeperBerth: '#3B82F6',
      driving: '#10B981',
      onDuty: '#F97316',
    },
  },
  typography: {
    fontFamily: "'Inter', 'Roboto', 'Helvetica', 'Arial', sans-serif",
    h1: { fontWeight: 700, letterSpacing: '-0.5px' },
    h2: { fontWeight: 700, letterSpacing: '-0.3px' },
    h3: { fontWeight: 600 },
    h4: { fontWeight: 600 },
    h5: { fontWeight: 600 },
    h6: { fontWeight: 600 },
    subtitle1: { fontWeight: 500 },
    subtitle2: { fontWeight: 500 },
    button: { fontWeight: 600, textTransform: 'none' },
    caption: { letterSpacing: '0.4px' },
  },
  shape: { borderRadius: 8 },
  components: {
    MuiAppBar: {
      styleOverrides: {
        root: {
          background: 'linear-gradient(135deg, #0D3B4E 0%, #1A5570 100%)',
          borderBottom: '3px solid #F59E0B',
        },
      },
    },
    MuiButton: {
      styleOverrides: {
        root: {
          borderRadius: 8,
          padding: '10px 24px',
          fontSize: '0.95rem',
        },
        contained: {
          '&.MuiButton-colorPrimary': {
            background: 'linear-gradient(135deg, #0D3B4E 0%, #1A5570 100%)',
            '&:hover': {
              background: 'linear-gradient(135deg, #082A38 0%, #0D3B4E 100%)',
            },
          },
        },
      },
    },
    MuiTextField: {
      styleOverrides: {
        root: {
          '& .MuiOutlinedInput-root': {
            borderRadius: 8,
            '&:hover fieldset': { borderColor: '#0D3B4E' },
            '&.Mui-focused fieldset': { borderColor: '#0D3B4E' },
          },
          '& .MuiInputLabel-root.Mui-focused': { color: '#0D3B4E' },
        },
      },
    },
    MuiCard: {
      styleOverrides: {
        root: {
          borderRadius: 8,
          border: '1px solid #E5E7EB',
          boxShadow: 'none',
        },
      },
    },
    MuiChip: {
      styleOverrides: {
        root: { borderRadius: 8 },
      },
    },
    MuiAlert: {
      styleOverrides: {
        root: { borderRadius: 8 },
      },
    },
    MuiPaper: {
      styleOverrides: {
        root: {
          borderRadius: 8,
          border: '1px solid #E5E7EB',
          boxShadow: 'none',
        },
      },
    },
  },
});

/** Theme with Driveline brand colors — responsive font sizes applied automatically */
export const theme = responsiveFontSizes(baseTheme);
