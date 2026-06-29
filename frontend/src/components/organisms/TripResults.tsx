import { Box, Typography, Stack, Paper } from '@mui/material';
import { LocalShipping, AccessTime, Speed, LocalGasStation, Hotel, Route } from '@mui/icons-material';
import { StatCard } from '@/components/atoms/StatCard';
import { SectionPaper } from '@/components/atoms/SectionPaper';
import { RouteMap } from '@/components/organisms/RouteMap';
import { LogbookCanvas } from '@/components/organisms/LogbookCanvas';
import { LogbookDayDetail } from '@/components/molecules/LogbookDayDetail';
import type { PlanRouteResponse } from '@/types/trip';
const DUTY_COLORS: Record<string, string> = {
  OFF_DUTY: '#6b7280',
  SLEEPER_BERTH: '#3b82f6',
  DRIVING: '#10B981',
  ON_DUTY_NOT_DRIVING: '#F97316',
};

export interface TripResultsProps {
  result: PlanRouteResponse;
}

export function TripResults({ result }: TripResultsProps) {

  const { trip_summary: summary, logbook_days: days, route_coordinates: coords, markers } = result;

  const stats = [
    { label: 'Total Distance', value: `${(summary?.total_distance_miles ?? 0).toLocaleString()} mi`, icon: <LocalShipping />, color: '#f59e0b' },
    { label: 'Trip Duration', value: `${(summary?.total_trip_hours ?? 0).toFixed(1)}h`, icon: <AccessTime />, color: '#f59e0b' },
    { label: 'Drive Time', value: `${(summary?.total_driving_hours ?? 0).toFixed(1)}h`, icon: <Speed />, color: '#22c55e' },
    { label: 'Fuel Stops', value: String(summary?.num_fuel_stops ?? 0), icon: <LocalGasStation />, color: '#f59e0b' },
    { label: 'Rest Stops', value: String(summary?.num_rest_stops ?? 0), icon: <Hotel />, color: '#3b82f6' },
    { label: 'Legs', value: `1 + ${(summary?.leg_1_miles ?? 0).toFixed(0)} / ${(summary?.leg_2_miles ?? 0).toFixed(0)} mi`, icon: <Route />, color: '#94a3b8' },
  ];

  const chartData = days.map((day) => ({
    name: `Day ${day.day}`,
    driving: day.row_totals.driving_hours,
    onDuty: day.row_totals.on_duty_not_driving_hours,
    sleeper: day.row_totals.sleeper_berth_hours,
    offDuty: day.row_totals.off_duty_hours,
  }));

  return (
    <Box>
      <Paper sx={{ p: 2, mb: 2 }}>
        <Stack direction="row" justifyContent="space-between" alignItems="center" sx={{ mb: 1 }}>
          <Typography variant="subtitle1" sx={{ fontWeight: 700, color: '#0D3B4E' }}>Trip Summary</Typography>
        </Stack>
        <Box sx={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(120px, 1fr))', gap: 1 }}>
          {stats.map((s, i) => (
            <StatCard key={s.label} icon={s.icon} label={s.label} value={s.value} delay={i * 0.08} />
          ))}
        </Box>
      </Paper>

      <SectionPaper title="Route Map">
        <RouteMap coords={coords} markers={markers} />
      </SectionPaper>

      <SectionPaper title="Daily Hours Breakdown">
        <Box sx={{ display: 'flex', gap: 2, flexWrap: 'wrap' }}>
          {chartData.map((d, i) => (
            <Box key={i} sx={{ flex: '1 1 150px', p: 1.5, bgcolor: '#f1f5f9', borderRadius: 1 }}>
              <Typography variant="caption" sx={{ fontWeight: 600, color: '#0f172a', mb: 1, display: 'block' }}>{d.name}</Typography>
              <Stack spacing={0.5}>
                {Object.entries({ driving: 'Driving', onDuty: 'On Duty', sleeper: 'Sleeper', offDuty: 'Off Duty' }).map(([key, label]) => (
                  <Box key={key} sx={{ display: 'flex', justifyContent: 'space-between' }}>
                    <Typography variant="caption" sx={{ color: DUTY_COLORS[key.toUpperCase()] }}>{label}</Typography>
                    <Typography variant="caption" sx={{ color: '#94a3b8' }}>{(d as any)[key].toFixed(1)}h</Typography>
                  </Box>
                ))}
              </Stack>
            </Box>
          ))}
        </Box>
      </SectionPaper>

      <SectionPaper title="ELD Logbook" subtitle={`${days.length} sheet${days.length > 1 ? 's' : ''}`}>
        <LogbookCanvas days={days} cycleSchedule={result.cycle_schedule} cycleMaxHours={result.cycle_max_hours} />
        <Box sx={{ mt: 2 }}>
          <LogbookDayDetail days={days} />
        </Box>
      </SectionPaper>
    </Box>
  );
}
