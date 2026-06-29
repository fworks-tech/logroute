import type { DutyStatus } from '@/types/trip';

/** Canvas and chip colour configuration for a single duty status. */
interface EldColorEntry {
  canvas: string;
  chip: { bgcolor: string; color: string };
}

type EldColors = Record<DutyStatus, EldColorEntry>;

const DEFAULT_COLORS: EldColors = {
  OFF_DUTY: { canvas: '#6B7280', chip: { bgcolor: 'rgba(107,114,128,0.2)', color: '#6B7280' } },
  SLEEPER_BERTH: { canvas: '#3B82F6', chip: { bgcolor: 'rgba(59,130,246,0.2)', color: '#3B82F6' } },
  DRIVING: { canvas: '#22C55E', chip: { bgcolor: 'rgba(34,197,94,0.2)', color: '#22C55E' } },
  ON_DUTY_NOT_DRIVING: { canvas: '#F59E0B', chip: { bgcolor: 'rgba(245,158,11,0.2)', color: '#F59E0B' } },
};

/** Hook returning the colour palette for ELD duty status display. */
export function useEldColors(): EldColors {
  return DEFAULT_COLORS;
}

export type { EldColors, EldColorEntry };
