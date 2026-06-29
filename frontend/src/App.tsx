import { useState, useEffect, useMemo, useRef } from 'react';
import Box from '@mui/material/Box';
import Drawer from '@mui/material/Drawer';
import IconButton from '@mui/material/IconButton';
import Tabs from '@mui/material/Tabs';
import Tab from '@mui/material/Tab';
import Typography from '@mui/material/Typography';
import Badge from '@mui/material/Badge';
import Popover from '@mui/material/Popover';
import Snackbar from '@mui/material/Snackbar';
import Alert from '@mui/material/Alert';
import useMediaQuery from '@mui/material/useMediaQuery';
import { useTheme } from '@mui/material/styles';
import MenuIcon from '@mui/icons-material/Menu';
import HistoryIcon from '@mui/icons-material/History';
import HelpOutlineIcon from '@mui/icons-material/HelpOutline';
import { Joyride } from 'react-joyride';
import { useTour } from '@/hooks/useTour';
import { TourTooltip } from '@/components/atoms/TourTooltip';
import { SHARED_OPTIONS } from '@/lib/tourConfig';
import { DivIcon } from 'leaflet';
import { MapContainer, TileLayer, Marker, Polyline, Popup, useMap } from 'react-leaflet';
import L from 'leaflet';
import { TripForm } from '@/components/organisms/TripForm';
import { TripResults } from '@/components/organisms/TripResults';
import { ErrorAlert } from '@/components/molecules/ErrorAlert';
import { SessionPanel } from '@/components/organisms/SessionPanel';
import { useTripPlanner } from '@/hooks/useTripPlanner';
import { useTripStore } from '@/store/tripStore';
import { MARKER_CONFIG } from '@/lib/mapConfig';
import type { RouteCoordinate } from '@/types/trip';
import type { TripFormValues } from '@/lib/schema';

const SIDEBAR_WIDTH = 440;
const MAP_BLUR_RADIUS = 10;
const DEFAULT_MAP_CENTER: [number, number] = [39.8283, -98.5795];
const MAP_FIT_BOUNDS_PADDING: [number, number] = [64, 64];
const MOBILE_MENU_BUTTON_OFFSET = 16;
const DESKTOP_DRAWER_MARGIN = 2;
const DESKTOP_DRAWER_VERTICAL_SPACE_PX = 32;

let autoSubmittedUrl = '';

/** Encodes trip form values into URL search parameters for sharing/bookmarking. */
function encodeFormToParams(data: TripFormValues): URLSearchParams {
  const p = new URLSearchParams();
  p.set('current', data.currentLocation);
  p.set('pickup', data.pickupLocation);
  p.set('dropoff', data.dropoffLocation);
  p.set('cycle', String(data.cycleHoursUsed));
  p.set('schedule', data.cycleSchedule);
  if (data.tripDate) p.set('date', data.tripDate);
  if (data.tractorNumber) p.set('tractor', data.tractorNumber);
  if (data.trailerNumber) p.set('trailer', data.trailerNumber);
  if (data.shipperName) p.set('shipper', data.shipperName);
  return p;
}

/** Decodes URL search parameters back into trip form values. */
function decodeParamsToForm(sp: URLSearchParams): TripFormValues | null {
  const current = sp.get('current');
  const pickup = sp.get('pickup');
  const dropoff = sp.get('dropoff');
  if (!current || !pickup || !dropoff) return null;
  return {
    currentLocation: current,
    pickupLocation: pickup,
    dropoffLocation: dropoff,
    cycleHoursUsed: parseFloat(sp.get('cycle') || '0') || 0,
    cycleSchedule: (sp.get('schedule') || '70') as '60' | '70',
    tripDate: sp.get('date') || '',
    tractorNumber: sp.get('tractor') || '',
    trailerNumber: sp.get('trailer') || '',
    shipperName: sp.get('shipper') || '',
  };
}

/** Adjusts the map viewport to fit all route coordinates. */
function SyncRouteViewport({ coordinates }: { coordinates: RouteCoordinate[] }) {
  const map = useMap();
  useEffect(() => {
    if (coordinates.length > 1) {
      map.fitBounds(coordinates.map((c) => [c.latitude, c.longitude] as [number, number]), { padding: MAP_FIT_BOUNDS_PADDING });
    } else if (coordinates.length === 1) {
      map.setView([coordinates[0].latitude, coordinates[0].longitude], 8);
    }
  }, [coordinates, map]);
  return null;
}

/** Renders a Leaflet legend control on the background map showing marker types. */
function BackgroundMapLegend() {
  const map = useMap();
  useEffect(() => {
    const LegendControl = L.Control.extend({
      onAdd: () => {
        const div = L.DomUtil.create('div', '');
        div.style.background = 'rgba(255,255,255,0.9)';
        div.style.border = '1px solid #e2e8f0';
        div.style.borderRadius = '6px';
        div.style.padding = '8px 10px';
        div.style.fontSize = '11px';
        div.style.minWidth = '100px';
        let html = '<div style="font-weight:700;margin-bottom:4px;color:#0D3B4E">Legend</div>';
        for (const cfg of Object.values(MARKER_CONFIG)) {
          html += `<div style="display:flex;align-items:center;gap:4px;margin-bottom:2px">` +
            `<span style="width:8px;height:8px;border-radius:50%;background:${cfg.bg};display:inline-block"></span>` +
            `<span style="color:#1f2937">${cfg.label}</span></div>`;
        }
        div.innerHTML = html;
        return div;
      },
    });
    const legend = new LegendControl({ position: 'topright' });
    legend.addTo(map);
    return () => { legend.remove(); };
  }, [map]);
  return null;
}

/** Root application component managing the sidebar, map, and trip planning workflow. */
export default function App() {
  const { submit, isLoading, error, reset, result } = useTripPlanner();
  const { sessionTrips, addSessionTrip, removeSessionTrip, clearSessionTrips } = useTripStore();
  const theme = useTheme();
  const isDesktop = useMediaQuery(theme.breakpoints.up('md'));
  const [mobileOpen, setMobileOpen] = useState(false);
  const [sidebarTab, setSidebarTab] = useState<'form' | 'results'>('form');
  const [toastOpen, setToastOpen] = useState(false);
  const [errorToastOpen, setErrorToastOpen] = useState(false);
  const [sessionAnchor, setSessionAnchor] = useState<HTMLButtonElement | null>(null);
  const lastFormValues = useRef<TripFormValues | null>(null);
  const lastResultRef = useRef<typeof result>(null);
  const lastErrorRef = useRef<typeof error>(null);

  const hasResult = !!result;
  const coordinates = result?.route_coordinates ?? [];
  const routePolyline = useMemo(() => coordinates.map((c) => [c.latitude, c.longitude] as [number, number]), [coordinates]);

  const tour = useTour();

  useEffect(() => {
    if (!tour.hasCompletedFormTour) {
      const timer = setTimeout(() => tour.startFormTour(), 1000);
      return () => clearTimeout(timer);
    }
  }, []);

  const prevResultRef = useRef<typeof result>(null);
  useEffect(() => {
    if (result && !prevResultRef.current && tour.hasCompletedFormTour && !tour.hasCompletedResultsTour && !tour.phase) {
      const timer = setTimeout(() => tour.startResultsTour(), 1000);
      prevResultRef.current = result;
      return () => clearTimeout(timer);
    }
    prevResultRef.current = result;
  }, [result]);

  useEffect(() => {
    if (result && lastResultRef.current !== result) {
      setToastOpen(true);
      lastResultRef.current = result;
      if (lastFormValues.current) {
        const fv = lastFormValues.current;
        addSessionTrip({
          id: crypto.randomUUID(),
          label: `${fv.pickupLocation} → ${fv.dropoffLocation}`,
          cycleHoursUsed: fv.cycleHoursUsed,
          drivingHours: result.trip_summary.total_driving_hours,
          totalMiles: result.trip_summary.total_distance_miles,
          plannedAt: new Date().toISOString(),
        });
      }
    }
  }, [result, addSessionTrip]);

  useEffect(() => {
    if (error && lastErrorRef.current !== error) {
      setErrorToastOpen(true);
      lastErrorRef.current = error;
    }
  }, [error]);

  const [initialValues, setInitialValues] = useState<TripFormValues | undefined>(() => {
    const sp = new URLSearchParams(window.location.search);
    return decodeParamsToForm(sp) ?? undefined;
  });

  useEffect(() => {
    const sp = new URLSearchParams(window.location.search);
    const qs = sp.toString();
    if (!qs || autoSubmittedUrl === qs) return;
    autoSubmittedUrl = qs;
    const values = decodeParamsToForm(sp);
    if (values) {
      lastFormValues.current = values;
      setSidebarTab('results');
      submit(values);
    }
  }, []);

  const handleFormSubmit = (data: TripFormValues) => {
    lastFormValues.current = data;
    setInitialValues(data);
    setSidebarTab('results');
    const params = encodeFormToParams(data);
    window.history.replaceState(null, '', `?${params.toString()}`);
    submit(data);
    if (!isDesktop) setMobileOpen(false);
  };

  const handleDismissError = () => {
    reset();
    setSidebarTab('form');
  };

  const handleRetry = () => {
    if (lastFormValues.current) {
      setSidebarTab('results');
      submit(lastFormValues.current);
    }
  };

  const drawerContent = (
    <Box sx={{ p: { xs: 2, sm: 2.5 }, height: '100%', overflowY: 'auto' }}>
      {isLoading && (
        <Box role="status" aria-live="polite" aria-atomic="true" sx={{ display: 'none' }}>
          Planning your route. Please wait.
        </Box>
      )}

      {error && (
        <Box sx={{ mb: 2 }}>
          <ErrorAlert
            error={error}
            onDismiss={handleDismissError}
            onRetry={error.isRetryable ? handleRetry : undefined}
          />
        </Box>
      )}

      <Box data-tour="welcome" sx={{ mb: 2, pb: 2, borderBottom: '1px solid', borderColor: 'divider' }}>
        <Box sx={{ mb: 1, display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
          <Typography variant="h6" sx={{ fontWeight: 700 }}>
            Trip Planner
          </Typography>
          <Box sx={{ display: 'flex', alignItems: 'center', gap: 0.5 }}>
            <IconButton
              size="small"
              aria-label="Start tour"
              onClick={tour.startFormTour}
              sx={{ color: '#94A3B8', '&:hover': { color: '#0D3B4E' } }}
            >
              <HelpOutlineIcon fontSize="small" />
            </IconButton>
            <IconButton
              size="small"
              aria-label="View session trips"
              data-tour="session-history"
              onClick={(e) => setSessionAnchor(e.currentTarget)}
            >
              <Badge badgeContent={sessionTrips.length} color="error" invisible={sessionTrips.length === 0}>
                <HistoryIcon fontSize="small" />
              </Badge>
            </IconButton>
          </Box>
        </Box>
        <Tabs
          value={sidebarTab}
          onChange={(_, newValue) => setSidebarTab(newValue)}
          variant="fullWidth"
          sx={{ minHeight: 40 }}
        >
          <Tab label="Plan Route" value="form" />
          <Tab label="Results" value="results" disabled={!result} />
        </Tabs>
      </Box>

      <Popover
        open={Boolean(sessionAnchor)}
        anchorEl={sessionAnchor}
        onClose={() => setSessionAnchor(null)}
        anchorOrigin={{ vertical: 'bottom', horizontal: 'right' }}
        transformOrigin={{ vertical: 'top', horizontal: 'right' }}
      >
        <SessionPanel
          trips={sessionTrips}
          onRemove={removeSessionTrip}
          onClear={() => {
            clearSessionTrips();
            setSessionAnchor(null);
          }}
        />
      </Popover>

      {sidebarTab === 'form' && (
        <TripForm
          onSubmit={handleFormSubmit}
          isLoading={isLoading}
          initialValues={initialValues}
        />
      )}
      {sidebarTab === 'results' && result && (
        <TripResults
          result={result}
        />
      )}
    </Box>
  );

  return (
    <Box
      sx={{
        position: 'relative',
        width: '100vw',
        height: '100vh',
        overflow: 'hidden',
        bgcolor: 'grey.900',
      }}
    >
      <Box
        component="a"
        href="#main-content"
        sx={{
          position: 'absolute',
          top: -40,
          left: 0,
          bgcolor: 'primary.main',
          color: 'white',
          p: 1,
          zIndex: (t) => t.zIndex.drawer + 2,
          textDecoration: 'none',
          '&:focus': {
            top: 0,
          },
        }}
      >
        Skip to main content
      </Box>

      {!isDesktop && (
        <IconButton
          aria-label="Open trip planning sidebar"
          data-testid="mobile-menu-toggle"
          onClick={() => setMobileOpen(true)}
          sx={{
            position: 'absolute',
            top: MOBILE_MENU_BUTTON_OFFSET,
            left: MOBILE_MENU_BUTTON_OFFSET,
            zIndex: (t) => t.zIndex.drawer + 1,
            bgcolor: 'rgba(255,255,255,0.92)',
            '&:hover': { bgcolor: 'rgba(255,255,255,1)' },
          }}
        >
          <MenuIcon />
        </IconButton>
      )}

      <Box
        aria-label="Trip route background map"
        data-testid="background-map-overlay"
        sx={{
          position: 'absolute',
          inset: 0,
          zIndex: 0,
          filter: hasResult ? 'blur(0px)' : `blur(${MAP_BLUR_RADIUS}px)`,
          transition: 'filter 0.5s ease',
          pointerEvents: hasResult ? 'auto' : 'none',
        }}
      >
        <MapContainer center={DEFAULT_MAP_CENTER} zoom={4} style={{ width: '100%', height: '100%' }}>
          <TileLayer
            url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
            attribution="&copy; OpenStreetMap contributors"
          />
          <SyncRouteViewport coordinates={coordinates} />
          <BackgroundMapLegend />
          {routePolyline.length > 0 && (
            <Polyline positions={routePolyline} color="#0D3B4E" weight={5} opacity={0.9} />
          )}
          {result?.markers?.map((marker, i) => {
            const cfg = MARKER_CONFIG[marker.type] ?? MARKER_CONFIG.start;
            return (
              <Marker
                key={marker.id || i}
                position={[marker.position.latitude, marker.position.longitude]}
                icon={
                  new DivIcon({
                    html: `<div role="img" aria-label="${cfg.label}" style="background-color:${cfg.bg};width:32px;height:32px;border-radius:50%;display:flex;align-items:center;justify-content:center;font-size:16px;border:2px solid white;box-shadow:0 2px 6px rgba(0,0,0,0.3)">${cfg.emoji}</div>`,
                    iconSize: [32, 32],
                    className: '',
                  })
                }
              >
                <Popup>
                  <Typography variant="subtitle2" sx={{ fontWeight: 600 }}>
                    {marker.label}
                  </Typography>
                  {marker.time && (
                    <Typography variant="caption" sx={{ color: 'text.secondary' }}>
                      {marker.time}
                    </Typography>
                  )}
                </Popup>
              </Marker>
            );
          })}
        </MapContainer>
      </Box>

      <Drawer
        anchor="left"
        open={isDesktop ? true : mobileOpen}
        onClose={() => setMobileOpen(false)}
        variant={isDesktop ? 'permanent' : 'temporary'}
        ModalProps={{ keepMounted: true }}
        sx={{
          zIndex: (t) => t.zIndex.drawer + 2,
          '& .MuiDrawer-paper': {
            width: SIDEBAR_WIDTH,
            maxWidth: '92vw',
            m: isDesktop ? DESKTOP_DRAWER_MARGIN : 0,
            borderRadius: isDesktop ? 2 : 0,
            height: isDesktop ? `calc(100% - ${DESKTOP_DRAWER_VERTICAL_SPACE_PX}px)` : '100%',
            bgcolor: 'rgba(255,255,255,0.95)',
            backdropFilter: 'blur(6px)',
            boxShadow: 8,
            border: '1px solid',
            borderColor: 'rgba(13,59,78,0.15)',
          },
        }}
      >
        <Box id="main-content" role="main">
          {drawerContent}
        </Box>
      </Drawer>

      <Snackbar
        open={toastOpen}
        autoHideDuration={5000}
        onClose={() => setToastOpen(false)}
        anchorOrigin={{ vertical: 'top', horizontal: 'right' }}
        role="status"
        aria-live="polite"
      >
        <Alert onClose={() => setToastOpen(false)} severity="success" sx={{ width: '100%' }}>
          <Typography variant="subtitle2" sx={{ fontWeight: 600, mb: 0.5 }}>
            Route planned!
          </Typography>
          <Typography variant="body2">
            {result?.logbook_days?.[0]?.from_location} → {result?.logbook_days?.[result.logbook_days.length - 1]?.to_location} · {Math.round(result?.trip_summary?.total_distance_miles ?? 0)} mi ·{' '}
            {(result?.trip_summary?.total_driving_hours ?? 0).toFixed(1)} hrs
          </Typography>
        </Alert>
      </Snackbar>

      <Snackbar
        open={errorToastOpen}
        autoHideDuration={7000}
        onClose={() => setErrorToastOpen(false)}
        anchorOrigin={{ vertical: 'top', horizontal: 'right' }}
        role="alert"
        aria-live="assertive"
      >
        <Alert onClose={() => setErrorToastOpen(false)} severity="error" sx={{ width: '100%' }}>
          <Typography variant="subtitle2" sx={{ fontWeight: 600, mb: 0.5 }}>
            Failed to plan route
          </Typography>
          <Typography variant="body2">
            {error?.message ?? 'Something went wrong. Please try again.'}
          </Typography>
        </Alert>
      </Snackbar>

      {tour.run && (
        <Joyride
          run={tour.run}
          steps={tour.steps}
          stepIndex={tour.stepIndex}
          continuous
          scrollToFirstStep
          tooltipComponent={TourTooltip}
          options={{
            primaryColor: SHARED_OPTIONS.primaryColor,
            textColor: SHARED_OPTIONS.textColor,
            backgroundColor: SHARED_OPTIONS.backgroundColor,
            arrowColor: SHARED_OPTIONS.arrowColor,
            overlayColor: SHARED_OPTIONS.overlayColor,
            spotlightRadius: SHARED_OPTIONS.spotlightRadius,
            width: SHARED_OPTIONS.width,
            zIndex: SHARED_OPTIONS.zIndex,
            showProgress: true,
            skipScroll: false,
          }}
          locale={{
            back: 'Back',
            close: 'Close',
            last: 'Done',
            next: 'Next',
            skip: 'Skip tour',
          }}
          onEvent={tour.handleCallback}
        />
      )}
    </Box>
  );
}
