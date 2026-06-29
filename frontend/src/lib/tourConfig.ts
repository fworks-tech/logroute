import type { Step } from 'react-joyride';

export const FORM_STEPS: Step[] = [
  {
    target: '[data-tour="welcome"]',
    title: 'Welcome to LogRoute',
    content:
      'Plan FMCSA-compliant trips, view ELD log sheets, and download DOT-ready PDFs — all in one click.',
    placement: 'bottom',
  },
  {
    target: '[data-tour="current-location"]',
    title: 'Current Location',
    content:
      'Start typing a city & state. The autocomplete searches OpenStreetMap in real time. Pick a suggestion or type a custom location.',
    placement: 'bottom',
  },
  {
    target: '[data-tour="pickup-location"]',
    title: 'Pickup Location',
    content:
      'Same autocomplete for your pickup. All three locations are required before the route can be planned.',
    placement: 'bottom',
  },
  {
    target: '[data-tour="dropoff-location"]',
    title: 'Dropoff Location',
    content:
      'The final stop. The backend will geocode all three, then fetch a route from OSRM.',
    placement: 'bottom',
  },
  {
    target: '[data-tour="cycle-hours"]',
    title: 'Cycle Hours Used',
    content:
      'Hours already logged in your current duty cycle. FMCSA caps: 70 hours over 8 days, or 60 over 7 — selectable below.',
    placement: 'bottom',
  },
  {
    target: '[data-tour="cycle-schedule"]',
    title: 'Cycle Schedule',
    content:
      'Choose 60-hr/7-day or 70-hr/8-day. This affects when the 34-hour restart triggers.',
    placement: 'bottom',
  },
  {
    target: '[data-tour="log-details"]',
    title: 'Optional Log Details',
    content:
      'Expand this to add trip date, tractor#, trailer#, and shipper name. These print directly onto the FMCSA log sheet.',
    placement: 'bottom',
  },
  {
    target: '[data-tour="quick-fills"]',
    title: 'Quick Examples',
    content:
      'Click one to pre-fill the form with a realistic route. Try it to see results instantly.',
    placement: 'bottom',
  },
  {
    target: '[data-tour="plan-button"]',
    title: 'Plan Route & Generate Logbook',
    content:
      'Sends everything to the backend. The HOS engine simulates your trip against all FMCSA rules and returns a full logbook.',
    placement: 'top',
  },
];

export const RESULTS_STEPS: Step[] = [
  {
    target: '[data-tour="download-pdf"]',
    title: 'Download Logbook PDF',
    content:
      'Export all logbook days as a single PDF, ready for inspection or filing.',
    placement: 'bottom',
  },
  {
    target: '[data-tour="trip-summary"]',
    title: 'Trip Summary',
    content:
      'Key stats at a glance: total distance, trip duration, drive time, fuel stops, rest stops, and leg breakdown.',
    placement: 'bottom',
  },
  {
    target: '[data-tour="route-map"]',
    title: 'Route Map',
    content:
      'The trip route drawn on an interactive Leaflet map. Markers show start, pickup, dropoff, fuel stops, and rest stops. Click any marker for details.',
    placement: 'left',
  },
  {
    target: '[data-tour="daily-breakdown"]',
    title: 'Daily Hours Breakdown',
    content:
      "Each day's duty hours split into Driving, On Duty, Sleeper Berth, and Off Duty. Colour-coded per FMCSA conventions.",
    placement: 'bottom',
  },
  {
    target: '[data-tour="logbook-sheet"]',
    title: 'ELD Logbook',
    content:
      'A rendered FMCSA §395.8 daily log sheet. Navigate between days using the tabs above. The canvas includes the 24-hour grid, duty bars, recap, and remarks.',
    placement: 'left',
  },
  {
    target: '[data-tour="logbook-day-nav"]',
    title: 'Day Navigation',
    content:
      'Use prev/next arrows or click a day tab to flip between logbook sheets. Each sheet is a separate page in the PDF export.',
    placement: 'bottom',
  },
  {
    target: '[data-tour="session-history"]',
    title: 'Session History',
    content:
      'Every trip you plan is saved here (persisted in your browser). Track cumulative cycle hours across multiple trips in one session.',
    placement: 'left',
  },
];

export const SHARED_OPTIONS = {
  primaryColor: '#0D3B4E',
  textColor: '#111827',
  backgroundColor: '#ffffff',
  arrowColor: '#ffffff',
  overlayColor: 'rgba(0,0,0,0.55)',
  spotlightRadius: 8,
  width: 380,
  zIndex: 1400,
};

export const STORAGE_KEY = 'logroute-tour';
