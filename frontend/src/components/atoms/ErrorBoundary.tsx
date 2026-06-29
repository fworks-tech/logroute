import React, { ReactNode } from 'react';
import Alert from '@mui/material/Alert';
import Button from '@mui/material/Button';
import Box from '@mui/material/Box';

interface Props { children: ReactNode; }
interface State { hasError: boolean; error: Error | null; }

/** React error boundary that catches rendering errors and displays a retry UI. */
export class ErrorBoundary extends React.Component<Props, State> {
  constructor(props: Props) {
    super(props);
    this.state = { hasError: false, error: null };
  }

  static getDerivedStateFromError(error: Error): State {
    return { hasError: true, error };
  }

  componentDidCatch(error: Error, errorInfo: React.ErrorInfo) {
    console.error('ErrorBoundary caught:', error, errorInfo);
  }

  handleReset = () => {
    this.setState({ hasError: false, error: null });
    window.location.reload();
  };

  render() {
    if (this.state.hasError) {
      return (
        <Box sx={{ p: 4, display: 'flex', flexDirection: 'column', alignItems: 'center', justifyContent: 'center', minHeight: '100vh' }}>
          <Alert severity="error" sx={{ mb: 2, maxWidth: 500 }}>
            Something went wrong. Please try refreshing the page.
          </Alert>
          <Button variant="contained" color="primary" onClick={this.handleReset}>
            Retry
          </Button>
        </Box>
      );
    }
    return this.props.children;
  }
}
