import type { TooltipRenderProps } from 'react-joyride';
import Paper from '@mui/material/Paper';
import Typography from '@mui/material/Typography';
import Button from '@mui/material/Button';
import Box from '@mui/material/Box';

export function TourTooltip({
  continuous,
  index,
  size,
  step,
  backProps,
  closeProps,
  primaryProps,
  skipProps,
  tooltipProps,
}: TooltipRenderProps) {
  return (
    <Paper
      elevation={8}
      sx={{
        maxWidth: 380,
        borderRadius: 2,
        overflow: 'hidden',
        border: 'none',
      }}
      {...tooltipProps}
    >
      <Box
        sx={{
          height: 4,
          bgcolor: 'brand.teal',
        }}
      />
      <Box sx={{ px: 2.5, py: 2 }}>
        {step.title && (
          <Typography variant="subtitle1" sx={{ fontWeight: 700, color: '#111827', mb: 1 }}>
            {step.title}
          </Typography>
        )}
        <Typography variant="body2" sx={{ color: '#4B5563', lineHeight: 1.6 }}>
          {step.content}
        </Typography>
      </Box>
      <Box
        sx={{
          px: 2.5,
          pb: 2,
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'space-between',
        }}
      >
        <Typography variant="caption" sx={{ color: '#94A3B8', fontWeight: 500 }}>
          {index + 1} of {size}
        </Typography>
        <Box sx={{ display: 'flex', gap: 0.5 }}>
          {index > 0 && (
            <Button size="small" variant="text" sx={{ color: '#64748B', fontWeight: 600, fontSize: 13 }} {...backProps}>
              Back
            </Button>
          )}
          {continuous && index < size - 1 && (
            <Button size="small" variant="contained" color="primary" sx={{ fontWeight: 600, fontSize: 13 }} {...primaryProps}>
              Next
            </Button>
          )}
          {index === size - 1 && (
            <Button size="small" variant="contained" color="primary" sx={{ fontWeight: 600, fontSize: 13 }} {...primaryProps}>
              Done
            </Button>
          )}
        </Box>
      </Box>
      <Box
        sx={{
          px: 2.5,
          pb: 1.5,
          display: 'flex',
          justifyContent: 'flex-end',
        }}
      >
        <Button size="small" variant="text" sx={{ color: '#94A3B8', fontWeight: 500, fontSize: 12 }} {...skipProps}>
          Skip tour
        </Button>
        <Button size="small" variant="text" sx={{ color: '#94A3B8', fontWeight: 500, fontSize: 12, ml: 1 }} {...closeProps}>
          Close
        </Button>
      </Box>
    </Paper>
  );
}
