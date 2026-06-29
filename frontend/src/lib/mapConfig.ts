/** Visual configuration for each marker type: background colour, emoji, and label text. */
export const MARKER_CONFIG: Record<string, { bg: string; emoji: string; label: string }> = {
  start: { bg: '#3B82F6', emoji: '📍', label: 'Start' },
  pickup: { bg: '#10B981', emoji: '📦', label: 'Pickup' },
  dropoff: { bg: '#EF4444', emoji: '🎯', label: 'Dropoff' },
  fuel: { bg: '#F59E0B', emoji: '⛽', label: 'Fuel Stop' },
  rest: { bg: '#8B5CF6', emoji: '😴', label: 'Rest' },
};
