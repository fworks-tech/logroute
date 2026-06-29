import Box from '@mui/material/Box';
import Typography from '@mui/material/Typography';
import Button from '@mui/material/Button';
import IconButton from '@mui/material/IconButton';
import Divider from '@mui/material/Divider';
import CloseIcon from '@mui/icons-material/Close';
import type { SessionTrip } from '@/store/tripStore';

interface SessionPanelProps {
  trips: SessionTrip[];
  onRemove: (id: string) => void;
  onClear: () => void;
}

export function SessionPanel({ trips, onRemove, onClear }: SessionPanelProps) {
  const last = trips[trips.length - 1];
  const totalHours = trips.length > 0
    ? last.cycleHoursUsed + trips.reduce((sum, t) => sum + t.drivingHours, 0)
    : 0;
  const isOverLimit = totalHours > 70;

  return (
    <Box sx={{ p: 2, minWidth: 280, maxWidth: 340 }}>
      <Typography variant="subtitle2" sx={{ fontWeight: 700, color: '#0f172a' }} gutterBottom>
        Session Trips ({trips.length})
      </Typography>
      <Divider sx={{ mb: 1 }} />
      {trips.map((trip, i) => (
        <Box key={trip.id} sx={{ mb: 1, display: 'flex', alignItems: 'flex-start', gap: 0.5 }}>
          <Box sx={{ flex: 1 }}>
            <Typography variant="caption" sx={{ fontWeight: 600, display: 'block', color: '#0f172a' }}>
              {i + 1}. {trip.label}
            </Typography>
            <Typography variant="caption" sx={{ color: '#64748b' }}>
              Started at {trip.cycleHoursUsed.toFixed(1)} hrs used · +{trip.drivingHours.toFixed(1)} hrs driving · {Math.round(trip.totalMiles)} mi
            </Typography>
          </Box>
          <IconButton size="small" onClick={() => onRemove(trip.id)} aria-label={`Remove trip ${i + 1}`} sx={{ mt: -0.25, color: '#64748b', '&:hover': { color: '#ef4444' } }}>
            <CloseIcon sx={{ fontSize: 14 }} />
          </IconButton>
        </Box>
      ))}
      <Divider sx={{ my: 1 }} />
      <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 1.5 }}>
        <Typography variant="caption" sx={{ fontWeight: 700, color: '#64748b' }}>Total hours this session</Typography>
        <Typography variant="caption" sx={{ fontWeight: 700 }} color={isOverLimit ? 'error.main' : '#0f172a'}>
          {totalHours.toFixed(1)} / 70 hrs
        </Typography>
      </Box>
      {isOverLimit && (
        <Typography variant="caption" color="error.main" sx={{ display: 'block', mb: 1 }}>
          Session total exceeds the 70-hour cycle limit.
        </Typography>
      )}
      <Button size="small" variant="outlined" onClick={onClear} fullWidth>
        Clear session
      </Button>
    </Box>
  );
}
