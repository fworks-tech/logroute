import React from 'react';
import { Alert, AlertTitle, Button, Box, Stack } from '@mui/material';
import type { ApiErrorResponse } from '@/types/trip';

export interface ErrorAlertProps {
  error: ApiErrorResponse | null;
  onRetry?: () => void;
  onDismiss?: () => void;
}

export const ErrorAlert: React.FC<ErrorAlertProps> = ({ error, onRetry, onDismiss }) => {
  if (!error) return null;
  const severity = error.code === 'validation_error' ? 'warning' : 'error';

  return (
    <Alert
      severity={severity}
      onClose={onDismiss}
      sx={{ mb: 2, display: 'flex', flexDirection: 'column', gap: 1 }}
      role="alert"
      aria-live="polite"
      aria-atomic="true"
    >
      <AlertTitle>{error.message}</AlertTitle>
      {error.detail && (
        <Box sx={{ fontSize: '0.875rem', color: 'inherit', opacity: 0.9 }}>
          {error.detail}
        </Box>
      )}
      {error.isRetryable && onRetry && (
        <Stack direction="row" spacing={1} sx={{ mt: 1 }}>
          <Button variant="outlined" size="small" onClick={onRetry} sx={{ borderColor: 'inherit', color: 'inherit' }}>
            Try again
          </Button>
          {onDismiss && (
            <Button variant="text" size="small" onClick={onDismiss} sx={{ color: 'inherit' }}>
              Dismiss
            </Button>
          )}
        </Stack>
      )}
    </Alert>
  );
};
