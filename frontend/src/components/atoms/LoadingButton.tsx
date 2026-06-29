import React from 'react';
import Button, { ButtonProps } from '@mui/material/Button';
import CircularProgress from '@mui/material/CircularProgress';
import Box from '@mui/material/Box';

export interface LoadingButtonProps extends ButtonProps {
  isLoading?: boolean;
  loadingLabel?: string;
}

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
