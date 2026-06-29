import { useEffect, useMemo } from 'react';
import { MapContainer, TileLayer, Marker, Polyline, Popup, useMap } from 'react-leaflet';
import L from 'leaflet';
import { Box, Typography } from '@mui/material';
import { MARKER_CONFIG } from '@/lib/mapConfig';
import type { Marker as RouteMarker, RouteCoordinate } from '@/types/trip';

/** Props for the RouteMap component. */
export interface RouteMapProps {
  coords: RouteCoordinate[];
  markers: RouteMarker[];
}

function createMarkerIcon(bg: string, initial: string) {
  return L.divIcon({
    className: '',
    iconSize: [32, 42],
    iconAnchor: [16, 42],
    popupAnchor: [0, -44],
    html: `<div style="position:relative;text-align:center" role="img" aria-label="${initial} marker">
      <svg width="32" height="42" viewBox="0 0 32 42" aria-hidden="true">
        <path d="M16 0C7.16 0 0 7.16 0 16c0 12 16 26 16 26s16-14 16-26C32 7.16 24.84 0 16 0z" fill="${bg}"/>
        <circle cx="16" cy="14" r="6" fill="#fff"/>
      </svg>
      <div style="position:absolute;top:14px;left:50%;transform:translateX(-50%);font-size:9px;font-weight:700;color:#fff;white-space:nowrap">${initial}</div>
    </div>`,
  });
}

function FitBounds({ coords }: { coords: [number, number][] }) {
  const map = useMap();
  useEffect(() => {
    if (coords.length > 0) {
      map.fitBounds(coords, { padding: [50, 50] });
    }
  }, [coords, map]);
  return null;
}

function MapLegend() {
  const map = useMap();

  useEffect(() => {
    const LegendControl = L.Control.extend({
      onAdd: () => {
        const div = L.DomUtil.create('div', '');
        div.setAttribute('role', 'region');
        div.setAttribute('aria-label', 'Map legend');
        div.style.background = 'rgba(255,255,255,0.95)';
        div.style.border = '1px solid #e2e8f0';
        div.style.borderRadius = '8px';
        div.style.padding = '10px 14px';
        div.style.color = '#1f2937';
        div.style.fontSize = '12px';
        div.style.fontWeight = '500';
        div.style.lineHeight = '1.6';
        div.style.minWidth = '130px';
        div.style.backdropFilter = 'blur(4px)';

        let html = '<div style="margin-bottom:6px;font-weight:700;font-size:13px;color:#0D3B4E">Legend</div>';
        html += '<div style="display:flex;align-items:center;gap:6px;margin-bottom:4px">' +
          '<span style="width:16px;height:3px;border-radius:2px;background:#f59e0b;display:inline-block"></span>' +
          '<span>Route</span></div>';

        for (const cfg of Object.values(MARKER_CONFIG)) {
          html += '<div style="display:flex;align-items:center;gap:6px;margin-bottom:2px">' +
            `<span style="width:10px;height:10px;border-radius:50%;background:${cfg.bg};display:inline-block"></span>` +
            `<span>${cfg.label}</span></div>`;
        }

        div.innerHTML = html;
        return div;
      },
    });

    const legend = new LegendControl({ position: 'bottomright' });
    legend.addTo(map);
    return () => { legend.remove(); };
  }, [map]);

  return null;
}

/** Interactive Leaflet map displaying the route polyline and markers with a legend. */
export function RouteMap({ coords, markers }: RouteMapProps) {
  const routePositions: [number, number][] = useMemo(
    () => coords.map((c) => [c.latitude, c.longitude]),
    [coords]
  );
  const center: [number, number] = routePositions.length > 0 ? routePositions[0] : [39.8283, -98.5795];

  return (
    <Box
      role="region"
      aria-label="Route map"
      sx={{
        height: 'clamp(300px, 40vh, 450px)',
        width: '100%',
        borderRadius: 1,
        overflow: 'hidden',
        position: 'relative',
      }}
    >
      <MapContainer
        center={center}
        zoom={6}
        style={{ height: '100%', width: '100%' }}
        zoomControl={false}
        aria-label="Interactive route map showing trip path and markers"
      >
        <TileLayer
          url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
          attribution='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'
        />

        <FitBounds coords={routePositions} />
        <MapLegend />

        <Polyline
          positions={routePositions}
          pathOptions={{ color: '#0D3B4E', weight: 4, opacity: 0.9 }}
          aria-label="Trip route"
        />

        {markers.map((m, i) => {
          const config = MARKER_CONFIG[m.type] || MARKER_CONFIG.start;
          return (
            <Marker
              key={m.id || i}
              position={[m.position.latitude, m.position.longitude]}
              icon={createMarkerIcon(config.bg, m.label.charAt(0))}
              aria-label={`${config.label}: ${m.label}`}
            >
              <Popup>
                <Typography variant="body2" sx={{ fontWeight: 600, color: '#111827' }}>
                  {m.label}
                </Typography>
                <Typography variant="caption" sx={{ color: '#6b7280', display: 'block' }}>
                  {config.label}
                </Typography>
                {m.time && (
                  <Typography variant="caption" sx={{ color: '#6b7280', display: 'block' }}>
                    {m.time}
                  </Typography>
                )}
              </Popup>
            </Marker>
          );
        })}
      </MapContainer>
    </Box>
  );
}
