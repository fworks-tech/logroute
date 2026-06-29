import React from 'react';
import Button, { ButtonProps } from '@mui/material/Button';
import CircularProgress from '@mui/material/CircularProgress';
import Box from '@mui/material/Box';

/** Props for the LoadingButton component, extending MUI Button props. */
export interface LoadingButtonProps extends ButtonProps {
  isLoading?: boolean;
  loadingLabel?: string;
}

/** Button that shows a loading spinner and custom label while in a pending state. */
export const LoadingButton: React.FC<LoadingButtonProps> = ({
  isLoading = false,
  loadingLabel = 'Loading…',
  children,
  disabled,
  ...rest
}) => (
  <Button {...rest} disabled={disabled || isLoading} aria-busy={isLoading} aria-label={isLoading ? loadingLabel : undefined}>
    {isLoading ? (
      <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
        <CircularProgress size={18} color="inherit" aria-hidden="true" />
        {loadingLabel}
      </Box>
    ) : children}
  </Button>
);
