import { useState, useEffect } from 'react';
import { useForm, Controller } from 'react-hook-form';
import { zodResolver } from '@hookform/resolvers/zod';
import Box from '@mui/material/Box';
import Typography from '@mui/material/Typography';
import TextField from '@mui/material/TextField';
import Autocomplete from '@mui/material/Autocomplete';
import Chip from '@mui/material/Chip';
import Divider from '@mui/material/Divider';
import Stack from '@mui/material/Stack';
import IconButton from '@mui/material/IconButton';
import Tooltip from '@mui/material/Tooltip';
import Collapse from '@mui/material/Collapse';
import Radio from '@mui/material/Radio';
import RadioGroup from '@mui/material/RadioGroup';
import FormControlLabel from '@mui/material/FormControlLabel';
import FormControl from '@mui/material/FormControl';
import FormLabel from '@mui/material/FormLabel';
import MyLocationIcon from '@mui/icons-material/MyLocation';
import LocalShippingIcon from '@mui/icons-material/LocalShipping';
import FlagIcon from '@mui/icons-material/Flag';
import AccessTimeIcon from '@mui/icons-material/AccessTime';
import ExpandMoreIcon from '@mui/icons-material/ExpandMore';
import HelpOutlineIcon from '@mui/icons-material/HelpOutlined';
import { useTripStore } from '@/store/tripStore';
import { tripSchema, TripFormValues } from '@/lib/schema';
import { LoadingButton } from '@/components/atoms/LoadingButton';
import { useGeocodeSearch } from '@/hooks/useGeocodeSearch';

const QUICK_FILLS = [
  { name: 'Chicago → Dallas', current: 'Chicago, IL', pickup: 'Chicago, IL', dropoff: 'Dallas, TX', cycle: 10 },
  { name: 'LA → Denver', current: 'Los Angeles, CA', pickup: 'Los Angeles, CA', dropoff: 'Denver, CO', cycle: 15 },
  { name: 'NY → Miami', current: 'New York, NY', pickup: 'New York, NY', dropoff: 'Miami, FL', cycle: 20 },
];

/** Props for the TripForm component. */
export interface TripFormProps {
  onSubmit: (data: TripFormValues) => void;
  isLoading: boolean;
  sidebarMode?: boolean;
  submittedValues?: TripFormValues;
  initialValues?: TripFormValues;
}

/** Trip planning form with geocoding autocomplete, cycle-hours input, and optional log details. */
export function TripForm({ onSubmit, isLoading, initialValues }: TripFormProps) {
  const [expandMetadata, setExpandMetadata] = useState(false);
  const currentGeocode = useGeocodeSearch();
  const pickupGeocode = useGeocodeSearch();
  const dropoffGeocode = useGeocodeSearch();

  const { control, handleSubmit, setValue, trigger, watch, formState: { errors, isValid } } = useForm<TripFormValues>({
    resolver: zodResolver(tripSchema),
    mode: 'all',
    defaultValues: initialValues ?? { currentLocation: '', pickupLocation: '', dropoffLocation: '', cycleHoursUsed: 0, cycleSchedule: '70', tripDate: '', tractorNumber: '', trailerNumber: '', shipperName: '' },
  });

  useEffect(() => {
    if (initialValues) {
      currentGeocode.setInputValue(initialValues.currentLocation);
      pickupGeocode.setInputValue(initialValues.pickupLocation);
      dropoffGeocode.setInputValue(initialValues.dropoffLocation);
    }
  }, []);

  const cycleValue = watch('cycleHoursUsed') || 0;
  const cycleSchedule = watch('cycleSchedule') || '70';
  const cycleMax = cycleSchedule === '60' ? 60 : 70;
  const sessionCycleTotal = useTripStore((s) => s.sessionCycleTotal());
  const isCycleFull = cycleValue >= cycleMax;
  const isCycleExceeded = cycleValue > cycleMax;

  const handleQuickFill = (fill: typeof QUICK_FILLS[number]) => {
    currentGeocode.setInputValue(fill.current);
    pickupGeocode.setInputValue(fill.pickup);
    dropoffGeocode.setInputValue(fill.dropoff);
    setValue('currentLocation', fill.current);
    setValue('pickupLocation', fill.pickup);
    setValue('dropoffLocation', fill.dropoff);
    setValue('cycleHoursUsed', fill.cycle);
    setValue('cycleSchedule', '70');
    trigger();
  };

  const geocodeInput = (name: 'currentLocation' | 'pickupLocation' | 'dropoffLocation', geocode: typeof currentGeocode, icon: React.ReactNode, label: string, placeholder: string) => (
    <Controller name={name} control={control} render={({ field: { onChange } }) => (
      <Autocomplete
        id={name}
        freeSolo
        disabled={isLoading}
        inputValue={geocode.inputValue}
        filterOptions={(x) => x}
        onChange={(_, v) => { const val = typeof v === 'string' ? v : v?.display_name ?? ''; onChange(val); geocode.setInputValue(val); }}
        onInputChange={(_, v, reason) => {
          if (reason === 'reset') return;
          onChange(v);
          geocode.setInputValue(v);
          geocode.search(v);
        }}
        options={geocode.suggestions as any[]}
        loading={geocode.isLoading}
        getOptionLabel={(o: any) => typeof o === 'string' ? o : o.display_name}
        noOptionsText={geocode.isLoading ? 'Searching...' : 'Type to search locations'}
        loadingText="Searching locations..."
        renderInput={(params) => (
          <TextField {...params} label={label} placeholder={placeholder} required disabled={isLoading}
            error={!!errors[name]} helperText={errors[name]?.message}
            InputProps={{ ...params.InputProps, startAdornment: <Box sx={{ mr: 1, color: '#94a3b8', display: 'flex' }}>{icon}</Box> }}
            inputProps={{ ...params.inputProps, 'aria-required': true }} />
        )}
      />
    )} />
  );

  return (
    <Box>
      {/* Quick fills */}
      <Box data-tour="quick-fills" sx={{ mb: 3 }}>
        <Typography variant="caption" sx={{ color: '#64748b', display: 'block', mb: 1 }}>Quick Examples</Typography>
        <Box sx={{ display: 'flex', flexWrap: 'wrap', gap: 1 }}>
          {QUICK_FILLS.map((fill) => (
            <Chip key={fill.name} label={fill.name} size="small" variant="outlined" onClick={() => handleQuickFill(fill)} disabled={isLoading}
              sx={{ cursor: 'pointer', '&:hover': { borderColor: '#0D3B4E', color: '#0D3B4E' } }} />
          ))}
        </Box>
      </Box>

      <Divider sx={{ mb: 3 }} />

      <Box component="form" onSubmit={handleSubmit(onSubmit)} noValidate>
        <Stack spacing={3}>
          <Box data-tour="current-location">{geocodeInput('currentLocation', currentGeocode, <MyLocationIcon />, 'Current Location', 'e.g., Chicago, IL')}</Box>
          <Box data-tour="pickup-location">{geocodeInput('pickupLocation', pickupGeocode, <LocalShippingIcon />, 'Pickup Location', 'e.g., Indianapolis, IN')}</Box>
          <Box data-tour="dropoff-location">{geocodeInput('dropoffLocation', dropoffGeocode, <FlagIcon />, 'Dropoff Location', 'e.g., Dallas, TX')}</Box>

          {/* Cycle Schedule + Hours */}
          <Box data-tour="cycle-hours">
            <Controller name="cycleHoursUsed" control={control} render={({ field }) => (
              <TextField {...field} id="cycleHoursUsed" label={
                <Box component="span" sx={{ display: 'flex', alignItems: 'center', gap: 0.5 }}>
                  Current Cycle Used (Hrs)
                  <Tooltip title={`FMCSA ${cycleMax}-hour / ${cycleSchedule === '60' ? 7 : 8}-day rule. Enter hours already used in current cycle.`} arrow placement="top">
                    <HelpOutlineIcon sx={{ fontSize: 16, color: '#94a3b8', cursor: 'help' }} />
                  </Tooltip>
                </Box>
              } type="number" fullWidth required disabled={isLoading} error={!!errors.cycleHoursUsed}
                helperText={errors.cycleHoursUsed?.message}
                slotProps={{ htmlInput: { min: 0, max: cycleMax - 0.5, step: 0.5 }, input: { startAdornment: <AccessTimeIcon sx={{ mr: 1, color: '#94a3b8' }} /> } }}
                onChange={(e) => field.onChange(parseFloat(e.target.value) || 0)} />
            )} />
                    <Box data-tour="cycle-schedule" sx={{ mt: 1, display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                      <Typography variant="caption" sx={{ color: '#94a3b8' }}>{cycleValue.toFixed(1)} / {cycleMax} hrs used</Typography>
                      <Controller name="cycleSchedule" control={control} render={({ field }) => (
                <FormControl size="small">
                  <FormLabel sx={{ fontSize: 11, color: '#64748b' }}>Cycle Schedule</FormLabel>
                  <RadioGroup row {...field} sx={{ gap: 0 }}>
                    <FormControlLabel value="60" control={<Radio size="small" sx={{ color: '#64748b', '&.Mui-checked': { color: '#f59e0b' } }} />}
                      label={<Typography variant="caption" sx={{ color: field.value === '60' ? '#f59e0b' : '#94a3b8' }}>60-hr / 7-day</Typography>} />
                    <FormControlLabel value="70" control={<Radio size="small" sx={{ color: '#64748b', '&.Mui-checked': { color: '#f59e0b' } }} />}
                      label={<Typography variant="caption" sx={{ color: field.value === '70' ? '#f59e0b' : '#94a3b8' }}>70-hr / 8-day</Typography>} />
                  </RadioGroup>
                </FormControl>
              )} />
            </Box>
            {sessionCycleTotal > 0 && (
              <Box sx={{ mt: 0.5, display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                <Typography variant="caption" sx={{ color: '#64748b' }}>Session total (previous trips)</Typography>
                <Typography variant="caption" sx={{ fontWeight: 600, color: sessionCycleTotal >= cycleMax ? '#ef4444' : '#10B981' }}>
                  {sessionCycleTotal.toFixed(1)} / {cycleMax} hrs
                </Typography>
              </Box>
            )}
            {isCycleExceeded && (
              <Typography variant="caption" sx={{ color: '#ef4444', display: 'block', mt: 0.5, fontWeight: 600 }}>
                ⚠ Cycle hours exceed the {cycleMax}-hour limit.
              </Typography>
            )}
            {isCycleFull && !isCycleExceeded && (
              <Typography variant="caption" sx={{ color: '#f59e0b', display: 'block', mt: 0.5, fontWeight: 600 }}>
                ⚠ Cycle limit of {cycleMax} hours reached. A 34-hour restart will be required.
              </Typography>
            )}
          </Box>

          {/* Optional Log Details */}
          <Box data-tour="log-details" sx={{ borderTop: '1px solid #e2e8f0', pt: 2 }}>
            <Box onClick={() => setExpandMetadata(!expandMetadata)} sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', cursor: 'pointer', p: 1, borderRadius: 1, '&:hover': { bgcolor: '#f1f5f9' } }}>
              <Typography variant="body2" sx={{ fontWeight: 600, color: '#64748b' }}>Log Details (Optional)</Typography>
              <IconButton size="small" sx={{ transform: expandMetadata ? 'rotate(180deg)' : 'rotate(0)', transition: 'transform 0.2s', color: '#64748b' }}>
                <ExpandMoreIcon fontSize="small" />
              </IconButton>
            </Box>
            <Collapse in={expandMetadata}>
              <Stack spacing={2} sx={{ mt: 2 }}>
                <Controller name="tripDate" control={control} render={({ field }) => (
                  <TextField {...field} id="tripDate" label="Trip Date" type="date" fullWidth disabled={isLoading}
                    slotProps={{ inputLabel: { shrink: true } }} />
                )} />
                <Controller name="tractorNumber" control={control} render={({ field }) => (
                  <TextField {...field} id="tractorNumber" label="Tractor Number" placeholder="e.g., TRAC-001" fullWidth disabled={isLoading} />
                )} />
                <Controller name="trailerNumber" control={control} render={({ field }) => (
                  <TextField {...field} id="trailerNumber" label="Trailer Number" placeholder="e.g., TRAIL-002" fullWidth disabled={isLoading} />
                )} />
                <Controller name="shipperName" control={control} render={({ field }) => (
                  <TextField {...field} id="shipperName" label="Shipper / Carrier Name" placeholder="e.g., Acme Corp" fullWidth disabled={isLoading} />
                )} />
              </Stack>
            </Collapse>
          </Box>

          <Box data-tour="plan-button"><LoadingButton type="submit" variant="contained" color="primary" fullWidth size="large" isLoading={isLoading}
            disabled={!isValid || isLoading}
            loadingLabel="Planning your route…"
            sx={{ mt: 1, py: 1.5, '&.Mui-disabled': { bgcolor: 'primary.main', color: 'primary.contrastText', opacity: 0.45 } }}>
            Plan Route & Generate Logbook
          </LoadingButton></Box>
        </Stack>
      </Box>
    </Box>
  );
}
