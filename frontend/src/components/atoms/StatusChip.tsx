import React from 'react';
import Chip from '@mui/material/Chip';
import type { DutyStatus } from '@/types/trip';
import { useEldColors } from '@/hooks';

const STATUS_LABELS: Record<DutyStatus, string> = {
  OFF_DUTY: 'Off Duty',
  SLEEPER_BERTH: 'Sleeper Berth',
  DRIVING: 'Driving',
  ON_DUTY_NOT_DRIVING: 'On Duty (Not Driving)',
};

/** Props for the StatusChip component. */
export interface StatusChipProps {
  status: DutyStatus;
}

/** Renders a coloured chip for a given ELD duty status. */
export const StatusChip: React.FC<StatusChipProps> = ({ status }) => {
  const eldColors = useEldColors();
  const label = STATUS_LABELS[status];
  const chipColors = eldColors[status].chip;

  return (
    <Chip label={label} size="small" aria-label={`Duty status: ${label}`} sx={{ ...chipColors, fontWeight: 600, fontSize: '0.75rem' }} />
  );
};
