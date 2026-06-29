import { test, expect, Page } from '@playwright/test';

const API_BASE = 'http://localhost:8000';

const MOCK_ROUTE_RESPONSE = {
  route_coordinates: Array.from({ length: 10 }, (_, i) => [-95.0 + i * 0.5, 40.0 + i * 0.5]),
  markers: [
    { lat: 41.8781, lon: -87.6298, type: 'start', label: 'Chicago, IL' },
    { lat: 41.8781, lon: -87.6298, type: 'pickup', label: 'Chicago, IL' },
    { lat: 32.7767, lon: -96.7970, type: 'dropoff', label: 'Dallas, TX' },
    { lat: 38.0, lon: -92.0, type: 'fuel', label: 'Fuel Stop' },
  ],
  logbook_days: [
    {
      day: 0, date_offset: 0, date: '06/29/2026',
      from_location: 'Chicago, IL', to_location: 'Dallas, TX',
      daily_miles: 925.0, cumulative_miles: 925.0,
      total_driving_hours: 11.0, total_on_duty_hours: 13.0,
      cycle_hours_after_day: 13.0,
      row_totals: { off_duty_hours: 11.0, sleeper_berth_hours: 0, driving_hours: 11.0, on_duty_not_driving_hours: 2.0 },
      events: [
        { status: 'DRIVING', start_time: '06:00', end_time: '11:00', duration_hours: 5.0, label: 'Driving to Pickup', location: '' },
        { status: 'ON_DUTY_NOT_DRIVING', start_time: '11:00', end_time: '12:00', duration_hours: 1.0, label: 'Pickup', location: 'Chicago, IL' },
        { status: 'DRIVING', start_time: '12:00', end_time: '18:00', duration_hours: 6.0, label: 'Driving to Dropoff', location: '' },
        { status: 'ON_DUTY_NOT_DRIVING', start_time: '18:00', end_time: '19:00', duration_hours: 1.0, label: 'Dropoff', location: 'Dallas, TX' },
        { status: 'OFF_DUTY', start_time: '19:00', end_time: '24:00', duration_hours: 5.0, label: 'Off Duty', location: '' },
      ],
    },
  ],
  trip_summary: {
    total_distance_miles: 925.0, total_trip_hours: 13.0, total_driving_hours: 11.0,
    total_drive_hours: 11.0, legs: 2, rest_stops: 0, fuel_stops: 1,
    num_fuel_stops: 1, num_rest_stops: 0, leg_1_miles: 465.0, leg_2_miles: 460.0,
  },
  trip_date: null, tractor_number: '', trailer_number: '', shipper_name: '',
  cycle_schedule: '70', cycle_max_hours: 70,
};

async function mockAllApi(page: Page) {
  await page.route(`${API_BASE}/api/plan-route/`, async (route) => {
    await route.fulfill({ status: 200, contentType: 'application/json', body: JSON.stringify(MOCK_ROUTE_RESPONSE) });
  });
  await page.route('**/api/geocode/*', async (route) => {
    await route.fulfill({ status: 200, contentType: 'application/json', body: JSON.stringify([]) });
  });
}

/** Simulate real user typing into an Autocomplete by accessible name */
async function fillAutocomplete(page: Page, label: string, value: string) {
  const input = page.getByRole('textbox', { name: new RegExp(label, 'i') });
  await input.click();
  await input.clear();
  await input.pressSequentially(value, { delay: 40 });
  await page.waitForTimeout(200);
  const listbox = page.locator('.MuiAutocomplete-listbox');
  const visible = await listbox.isVisible({ timeout: 2000 }).catch(() => false);
  if (visible) {
    await page.keyboard.press('Escape');
  }
  await page.keyboard.press('Tab');
  await page.waitForTimeout(100);
}

/** Mock geocode to return realistic suggestions so the user can select from them */
async function mockGeocodeResults(page: Page) {
  await page.route('**/api/geocode/*', async (route) => {
    const url = new URL(route.request().url());
    const q = url.searchParams.get('q') || '';
    const mockResults = [
      { display_name: `${q}, IL, United States`, lat: 40.0, lon: -90.0, osm_id: 1 },
    ];
    await route.fulfill({ status: 200, contentType: 'application/json', body: JSON.stringify(mockResults) });
  });
}

test.describe('Trip Planning Page', () => {

  test('loads with dark map background and light sidebar', async ({ page }) => {
    await page.goto('/');
    await expect(page.locator('.leaflet-container')).toBeVisible();
    await expect(page.locator('.MuiDrawer-paper')).toBeVisible();
    await expect(page.getByText('LogRoute')).toBeVisible();
    await expect(page.getByRole('tab', { name: 'Plan' })).toBeVisible();
  });

  test('shows form inputs on load', async ({ page }) => {
    await page.goto('/');
    await expect(page.getByLabel('Current Location')).toBeVisible();
    await expect(page.getByLabel('Pickup Location')).toBeVisible();
    await expect(page.getByLabel('Dropoff Location')).toBeVisible();
    await expect(page.getByLabel(/Current Cycle Used/)).toBeVisible();
    await expect(page.getByText('Plan Route & Generate Logbook')).toBeVisible();
    await expect(page.getByText('Chicago → Dallas')).toBeVisible();
    await expect(page.getByText('LA → Denver')).toBeVisible();
    await expect(page.getByText('NY → Miami')).toBeVisible();
  });

  test('quick fill populates form fields', async ({ page }) => {
    await page.goto('/');
    await page.getByText('Chicago → Dallas').click();
    await page.waitForTimeout(500);
    await expect(page.getByRole('textbox', { name: /Current Location/ })).toHaveValue('Chicago, IL');
    await expect(page.getByRole('textbox', { name: /Dropoff Location/ })).toHaveValue('Dallas, TX');
  });

  test('cycle schedule toggle switches between 60/7 and 70/8', async ({ page }) => {
    await page.goto('/');
    await expect(page.getByText('70-hr / 8-day')).toBeVisible();
    await expect(page.locator('input[value="70"]')).toBeChecked();
    await page.locator('input[value="60"]').click();
    await expect(page.locator('input[value="60"]')).toBeChecked();
    await expect(page.locator('input[value="70"]')).not.toBeChecked();
    await page.locator('input[value="70"]').click();
    await expect(page.locator('input[value="70"]')).toBeChecked();
  });

  test('shows validation error on short input', async ({ page }) => {
    await page.goto('/');
    const input = page.getByRole('textbox', { name: /Current Location/ });
    await input.click();
    await input.pressSequentially('A', { delay: 30 });
    await page.keyboard.press('Tab');
    await expect(page.getByText('Location required').first()).toBeVisible({ timeout: 3000 });
  });

  test('autocomplete shows suggestions and user can select from them', async ({ page }) => {
    await mockGeocodeResults(page);
    await page.goto('/');
    const input = page.getByRole('textbox', { name: /Current Location/ });
    await input.click();
    await input.pressSequentially('Chic', { delay: 50 });
    const listbox = page.locator('.MuiAutocomplete-listbox');
    await expect(listbox).toBeVisible({ timeout: 5000 });
    await listbox.locator('li').first().click();
    await expect(input).toHaveValue(/Chic/);
  });

  test('plans a route successfully and shows results', async ({ page }) => {
    await mockAllApi(page);
    await page.goto('/');
    await fillAutocomplete(page, 'currentLocation', 'Chicago, IL');
    await fillAutocomplete(page, 'pickupLocation', 'Chicago, IL');
    await fillAutocomplete(page, 'dropoffLocation', 'Dallas, TX');
    await page.getByLabel(/Current Cycle Used/).click();
    await page.getByLabel(/Current Cycle Used/).fill('10');
    await page.getByRole('button', { name: 'Plan Route & Generate Logbook' }).click();
    await expect(page.getByText('Trip Summary')).toBeVisible({ timeout: 15000 });
    await expect(page.getByText('Total Distance')).toBeVisible();
    await expect(page.getByText('Trip Duration')).toBeVisible();
    await expect(page.locator('.leaflet-container')).toBeVisible();
    await expect(page.getByText('ELD Logbook')).toBeVisible();
  });

  test('route results include fuel stop markers on map', async ({ page }) => {
    await mockAllApi(page);
    await page.goto('/');
    await fillAutocomplete(page, 'currentLocation', 'Chicago, IL');
    await fillAutocomplete(page, 'pickupLocation', 'Chicago, IL');
    await fillAutocomplete(page, 'dropoffLocation', 'Dallas, TX');
    await page.getByLabel(/Current Cycle Used/).click();
    await page.getByLabel(/Current Cycle Used/).fill('10');
    await page.getByRole('button', { name: 'Plan Route & Generate Logbook' }).click();
    await expect(page.getByText('Fuel Stop').first()).toBeVisible({ timeout: 15000 });
  });

  test('shows error alert on API failure', async ({ page }) => {
    await page.route(`${API_BASE}/api/plan-route/`, async (route) => {
      await route.fulfill({ status: 502, contentType: 'application/json', body: JSON.stringify({ error: 'Service unavailable' }) });
    });
    await page.route('**/api/geocode/*', async (route) => {
      await route.fulfill({ status: 200, contentType: 'application/json', body: JSON.stringify([]) });
    });
    await page.goto('/');
    await fillAutocomplete(page, 'currentLocation', 'Chicago, IL');
    await fillAutocomplete(page, 'pickupLocation', 'Chicago, IL');
    await fillAutocomplete(page, 'dropoffLocation', 'Dallas, TX');
    await page.getByLabel(/Current Cycle Used/).click();
    await page.getByLabel(/Current Cycle Used/).fill('10');
    await page.getByRole('button', { name: 'Plan Route & Generate Logbook' }).click();
    await expect(page.getByText('Service unavailable')).toBeVisible({ timeout: 15000 });
  });

  test('session history stores completed trips', async ({ page }) => {
    await mockAllApi(page);
    await page.goto('/');
    await fillAutocomplete(page, 'currentLocation', 'Chicago, IL');
    await fillAutocomplete(page, 'pickupLocation', 'Chicago, IL');
    await fillAutocomplete(page, 'dropoffLocation', 'Dallas, TX');
    await page.getByLabel(/Current Cycle Used/).click();
    await page.getByLabel(/Current Cycle Used/).fill('10');
    await page.getByRole('button', { name: 'Plan Route & Generate Logbook' }).click();
    await expect(page.getByText('Trip Summary')).toBeVisible({ timeout: 15000 });
    await page.getByLabel('View session trips').click();
    await expect(page.getByText(/925\.0.*mi/)).toBeVisible();
  });

  test('log details expand/collapse works', async ({ page }) => {
    await page.goto('/');
    await page.getByText('Log Details (Optional)').click();
    await expect(page.getByLabel('Trip Date')).toBeVisible();
    await expect(page.getByLabel('Tractor Number')).toBeVisible();
    await expect(page.getByLabel('Trailer Number')).toBeVisible();
    await expect(page.getByLabel('Shipper / Carrier Name')).toBeVisible();
    await page.getByText('Log Details (Optional)').click();
    await expect(page.getByLabel('Trip Date')).not.toBeVisible();
  });

  test('responsive: mobile viewport shows hamburger menu', async ({ page }) => {
    await page.setViewportSize({ width: 375, height: 667 });
    await page.goto('/');
    await expect(page.getByLabel('Open sidebar')).toBeVisible();
    await page.getByLabel('Open sidebar').click();
    await expect(page.locator('.MuiDrawer-paper')).toBeVisible();
  });
});
