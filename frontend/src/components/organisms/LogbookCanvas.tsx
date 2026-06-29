import { useRef, useEffect, useCallback, forwardRef, useImperativeHandle } from 'react';
import { Box, Stack, IconButton, Tabs, Tab } from '@mui/material';
import { ChevronLeft, ChevronRight } from '@mui/icons-material';
import { useEldColors } from '@/hooks/useEldColors';
import { useLogbookNavigation } from '@/hooks/useLogbookNavigation';
import type { LogbookDay, LogbookEvent, DutyStatus } from '@/types/trip';

/** Ref handle exposed by LogbookCanvas for exporting the logbook sheet as PDF. */
export interface LogbookCanvasHandle {
  exportPdf: () => Promise<void>;
}

/** Props for the LogbookCanvas component. */
interface LogbookCanvasProps {
  day?: LogbookDay;
  days?: LogbookDay[];
  cycleSchedule?: string;
  cycleMaxHours?: number;
  tractorNumber?: string;
  trailerNumber?: string;
  shipperName?: string;
  tripDate?: string;
}

const DUTY_LABELS: Record<DutyStatus, string> = {
  OFF_DUTY: 'OFF DUTY',
  SLEEPER_BERTH: 'SLEEPER BERTH',
  DRIVING: 'DRIVING',
  ON_DUTY_NOT_DRIVING: 'ON DUTY (NOT DRIVING)',
};

const DUTY_ROWS: DutyStatus[] = ['OFF_DUTY', 'SLEEPER_BERTH', 'DRIVING', 'ON_DUTY_NOT_DRIVING'];

const CANVAS_WIDTH = 960;
const CANVAS_HEIGHT = 780;
const LEFT_LABEL_W = 76;
const GRID_LEFT = LEFT_LABEL_W;
const HOUR_W = 30;
const GRID_W = HOUR_W * 24;
const ROW_H = 54;
const GRID_TOP = 118;
const GRID_BOTTOM = GRID_TOP + DUTY_ROWS.length * ROW_H;
const HEADER_TITLE_Y = 16;
const HEADER_FIELD_Y = 34;
const REMARKS_TOP = GRID_BOTTOM + 16;
const RECAP_TOP = REMARKS_TOP + 130;
const FOOTER_TOP = RECAP_TOP + 110;
const RIGHT_TOTALS_X = GRID_LEFT + GRID_W + 6;

function timeToH(timeStr: string): number {
  const [h, m] = timeStr.split(':').map(Number);
  return h + (m || 0) / 60;
}

function drawGrid(ctx: CanvasRenderingContext2D) {
  ctx.save();

  for (let r = 0; r <= DUTY_ROWS.length; r++) {
    const y = GRID_TOP + r * ROW_H;
    ctx.beginPath();
    ctx.moveTo(GRID_LEFT, y);
    ctx.lineTo(GRID_LEFT + GRID_W, y);
    ctx.strokeStyle = '#000000';
    ctx.lineWidth = r === 0 || r === DUTY_ROWS.length ? 1.5 : 1;
    ctx.stroke();

    if (r < DUTY_ROWS.length) {
      const labelY = GRID_TOP + r * ROW_H + ROW_H / 2;
      ctx.fillStyle = '#000000';
      ctx.font = 'bold 10px "Inter", "Courier New", monospace';
      ctx.textAlign = 'right';
      ctx.textBaseline = 'middle';
      ctx.fillText(DUTY_LABELS[DUTY_ROWS[r]], GRID_LEFT - 6, labelY);
    }
  }

  for (let h = 0; h <= 24; h++) {
    const x = GRID_LEFT + h * HOUR_W;
    ctx.beginPath();
    ctx.moveTo(x, GRID_TOP);
    ctx.lineTo(x, GRID_BOTTOM);
    ctx.strokeStyle = h % 4 === 0 ? '#000000' : '#555555';
    ctx.lineWidth = h % 4 === 0 ? 1.2 : 0.5;
    ctx.stroke();

    if (h < 24) {
      const cx = x + HOUR_W / 2;
      for (let m = 1; m <= 3; m++) {
        const tx = GRID_LEFT + (h + m / 4) * HOUR_W;
        ctx.beginPath();
        ctx.moveTo(tx, GRID_TOP);
        ctx.lineTo(tx, GRID_TOP + 6);
        ctx.strokeStyle = '#888888';
        ctx.lineWidth = 0.5;
        ctx.stroke();
        ctx.beginPath();
        ctx.moveTo(tx, GRID_BOTTOM);
        ctx.lineTo(tx, GRID_BOTTOM - 6);
        ctx.stroke();
      }

      ctx.fillStyle = '#000000';
      ctx.font = 'bold 9px "Inter", "Courier New", monospace';
      ctx.textAlign = 'center';
      ctx.textBaseline = 'bottom';
      ctx.fillText(String(h), cx, GRID_TOP - 4);
    }
  }

  ctx.restore();
}

function drawHeader(ctx: CanvasRenderingContext2D, day: LogbookDay, tractorNumber?: string, trailerNumber?: string, shipperName?: string) {
  ctx.save();

  ctx.fillStyle = '#000000';
  ctx.font = 'bold 14px "Inter", "Courier New", monospace';
  ctx.textAlign = 'center';
  ctx.textBaseline = 'top';
  ctx.fillText("DRIVER'S RECORD OF DUTY STATUS (FMCSA §395.8)", CANVAS_WIDTH / 2, HEADER_TITLE_Y + 2);

  ctx.font = 'bold 18px "Inter", "Courier New", monospace';
  ctx.fillText(shipperName || 'LOGROUTE TRANSPORT', CANVAS_WIDTH / 2, HEADER_TITLE_Y + 20);

  ctx.font = '10px "Inter", "Courier New", monospace';
  ctx.textAlign = 'left';
  ctx.textBaseline = 'top';
  ctx.fillText(`Date: ${day.date}`, 14, HEADER_FIELD_Y + 20);
  ctx.fillText(`From: ${day.from_location}`, 14, HEADER_FIELD_Y + 34);
  ctx.fillText(`To:   ${day.to_location}`, 14, HEADER_FIELD_Y + 48);

  ctx.textAlign = 'right';
  ctx.fillText(`Tractor #: ${tractorNumber || '_______________'}`, CANVAS_WIDTH - 14, HEADER_FIELD_Y + 20);
  ctx.fillText(`Trailer #: ${trailerNumber || '_______________'}`, CANVAS_WIDTH - 14, HEADER_FIELD_Y + 34);
  ctx.fillText(`Shipper:  ${shipperName || '_______________'}`, CANVAS_WIDTH - 14, HEADER_FIELD_Y + 48);

  ctx.textAlign = 'left';
  ctx.font = 'bold 10px "Inter", "Courier New", monospace';
  ctx.fillText(`Miles Today: ${day.daily_miles.toFixed(0)} mi`, 14, HEADER_FIELD_Y + 66);
  ctx.fillText(`Driving Today: ${day.total_driving_hours.toFixed(1)} hrs`, 14, HEADER_FIELD_Y + 80);
  ctx.fillText('Co-Driver: _______________  Time Zone: Local  Shipping Doc: _______________', 14, HEADER_FIELD_Y + 94);

  ctx.strokeStyle = '#000000';
  ctx.lineWidth = 2;
  ctx.beginPath();
  ctx.moveTo(10, GRID_TOP - 8);
  ctx.lineTo(CANVAS_WIDTH - 10, GRID_TOP - 8);
  ctx.stroke();

  ctx.restore();
}

function drawEvents(ctx: CanvasRenderingContext2D, events: LogbookEvent[], eldColors: Record<string, { canvas: string }>) {
  ctx.save();

  for (const event of events) {
    const rowIdx = DUTY_ROWS.indexOf(event.status);
    if (rowIdx === -1) continue;

    const startH = timeToH(event.start_time);
    const endH = timeToH(event.end_time);
    if (endH <= startH) continue;

    const x1 = GRID_LEFT + startH * HOUR_W;
    const x2 = GRID_LEFT + endH * HOUR_W;
    const y = GRID_TOP + rowIdx * ROW_H + 5;
    const h = ROW_H - 10;
    const w = Math.max(x2 - x1, 2);

    const color = eldColors[event.status]?.canvas || '#6B7280';
    ctx.fillStyle = color;
    ctx.fillRect(x1, y, w, h);

    ctx.strokeStyle = '#000000';
    ctx.lineWidth = 0.5;
    ctx.strokeRect(x1, y, w, h);

    if (w > 28) {
      ctx.fillStyle = event.status === 'ON_DUTY_NOT_DRIVING' ? '#000000' : '#ffffff';
      ctx.font = 'bold 9px "Inter", "Courier New", monospace';
      ctx.textAlign = 'center';
      ctx.textBaseline = 'middle';
      const dur = event.duration_hours.toFixed(1);
      ctx.fillText(`${dur}h`, (x1 + x2) / 2, y + h / 2);
    }
  }

  ctx.restore();
}

function drawRowTotals(ctx: CanvasRenderingContext2D, day: LogbookDay) {
  ctx.save();

  const totals: Record<DutyStatus, number> = {
    OFF_DUTY: day.row_totals.off_duty_hours,
    SLEEPER_BERTH: day.row_totals.sleeper_berth_hours,
    DRIVING: day.row_totals.driving_hours,
    ON_DUTY_NOT_DRIVING: day.row_totals.on_duty_not_driving_hours,
  };

  ctx.fillStyle = '#000000';
  ctx.font = 'bold 10px "Inter", "Courier New", monospace';
  ctx.textAlign = 'left';
  ctx.textBaseline = 'middle';

  ctx.fillText('TOTAL', RIGHT_TOTALS_X, GRID_TOP - 6);

  for (let r = 0; r < DUTY_ROWS.length; r++) {
    const status = DUTY_ROWS[r];
    const val = totals[status];
    const y = GRID_TOP + r * ROW_H + ROW_H / 2;
    ctx.fillText(`${val.toFixed(1)}h`, RIGHT_TOTALS_X, y);
  }

  ctx.restore();
}

function drawRemarks(ctx: CanvasRenderingContext2D, day: LogbookDay) {
  ctx.save();

  ctx.strokeStyle = '#000000';
  ctx.lineWidth = 1.5;
  ctx.beginPath();
  ctx.moveTo(14, REMARKS_TOP - 6);
  ctx.lineTo(CANVAS_WIDTH - 14, REMARKS_TOP - 6);
  ctx.stroke();

  ctx.fillStyle = '#000000';
  ctx.font = 'bold 11px "Inter", "Courier New", monospace';
  ctx.textAlign = 'left';
  ctx.textBaseline = 'top';
  ctx.fillText('REMARKS (FMCSA §395.8):', 14, REMARKS_TOP);

  ctx.font = '10px "Inter", "Courier New", monospace';
  const remarks = day.events.filter((e) => e.label || e.location);
  if (remarks.length > 0) {
    remarks.slice(0, 6).forEach((e, i) => {
      const text = `${e.start_time}-${e.end_time} ${e.label || e.location || ''}`;
      ctx.fillText(text, 14, REMARKS_TOP + 16 + i * 15);
    });
  } else {
    ctx.fillStyle = '#888888';
    ctx.font = 'italic 10px "Inter", "Courier New", monospace';
    ctx.fillText('No remarks recorded for this day.', 14, REMARKS_TOP + 16);
  }

  ctx.fillStyle = '#000000';
  ctx.font = '10px "Inter", "Courier New", monospace';
  ctx.fillText("Driver's Signature: __________________________", 14, REMARKS_TOP + 110);

  ctx.restore();
}

function drawRecap(ctx: CanvasRenderingContext2D, day: LogbookDay, cycleSchedule?: string, cycleMaxHours?: number) {
  ctx.save();

  const schedule = cycleSchedule || '70';
  const maxHours = cycleMaxHours || 70;
  const cycleDays = schedule === '60' ? 7 : 8;
  const title = `RECAP — ${maxHours} HOUR / ${cycleDays} DAY CYCLE`;

  ctx.strokeStyle = '#000000';
  ctx.lineWidth = 1.5;
  ctx.beginPath();
  ctx.moveTo(14, RECAP_TOP - 6);
  ctx.lineTo(CANVAS_WIDTH - 14, RECAP_TOP - 6);
  ctx.stroke();

  ctx.fillStyle = '#000000';
  ctx.font = 'bold 11px "Inter", "Courier New", monospace';
  ctx.textAlign = 'left';
  ctx.textBaseline = 'top';
  ctx.fillText(title, 14, RECAP_TOP);

  const totalOnDuty = day.row_totals.driving_hours + day.row_totals.on_duty_not_driving_hours;
  const availTomorrow = Math.max(0, 14 - totalOnDuty);
  const availAfterRestart = Math.max(0, maxHours - (day.cycle_hours_after_day || 0));

  ctx.font = '10px "Inter", "Courier New", monospace';
  const recapLines = [
    `A — On Duty Today: ${totalOnDuty.toFixed(1)} hrs`,
    `B — Available Tomorrow: ${availTomorrow.toFixed(1)} hrs (14-hr rule)`,
    `C — Avail. After 34hr Restart: ${availAfterRestart.toFixed(1)} hrs (${maxHours}-hr / ${cycleDays}-day rule)`,
  ];

  recapLines.forEach((line, i) => {
    ctx.fillText(line, 14, RECAP_TOP + 16 + i * 16);
    ctx.beginPath();
    ctx.moveTo(14, RECAP_TOP + 28 + i * 16);
    ctx.lineTo(CANVAS_WIDTH - 14, RECAP_TOP + 28 + i * 16);
    ctx.strokeStyle = '#cccccc';
    ctx.lineWidth = 0.5;
    ctx.stroke();
  });

  ctx.fillStyle = '#000000';
  ctx.font = 'bold 10px "Inter", "Courier New", monospace';
  ctx.fillText('Cycle Hours Used So Far:', 14, RECAP_TOP + 74);
  ctx.font = '10px "Inter", "Courier New", monospace';
  ctx.fillText(`${(day.cycle_hours_after_day || 0).toFixed(1)} hrs`, 180, RECAP_TOP + 74);

  ctx.restore();
}

function drawFooter(ctx: CanvasRenderingContext2D) {
  ctx.save();

  ctx.strokeStyle = '#000000';
  ctx.lineWidth = 1;
  ctx.beginPath();
  ctx.moveTo(14, FOOTER_TOP - 4);
  ctx.lineTo(CANVAS_WIDTH - 14, FOOTER_TOP - 4);
  ctx.stroke();

  ctx.fillStyle = '#555555';
  ctx.font = '8px "Inter", "Courier New", monospace';
  ctx.textAlign = 'right';
  ctx.textBaseline = 'bottom';
  ctx.fillText('Form LM-1 (FMCSA §395.8) — LogRoute Transport v1.0', CANVAS_WIDTH - 14, FOOTER_TOP + 4);

  ctx.restore();
}

function renderCanvas(ctx: CanvasRenderingContext2D, day: LogbookDay, eldColors: ReturnType<typeof useEldColors>, cycleSchedule?: string, cycleMaxHours?: number, tractorNumber?: string, trailerNumber?: string, shipperName?: string) {
  ctx.fillStyle = '#ffffff';
  ctx.fillRect(0, 0, CANVAS_WIDTH, CANVAS_HEIGHT);

  drawHeader(ctx, day, tractorNumber, trailerNumber, shipperName);
  drawGrid(ctx);
  drawEvents(ctx, day.events, eldColors);
  drawRowTotals(ctx, day);
  drawRemarks(ctx, day);
  drawRecap(ctx, day, cycleSchedule, cycleMaxHours);
  drawFooter(ctx);
}

/** Canvas rendering of an FMCSA ELD logbook sheet with grid, events, recap, and remarks. */
export const LogbookCanvas = forwardRef<LogbookCanvasHandle, LogbookCanvasProps>(function LogbookCanvas(
  { day, days, cycleSchedule, cycleMaxHours, tractorNumber, trailerNumber, shipperName },
  ref,
) {
  const canvasRef = useRef<HTMLCanvasElement>(null);
  const eldColors = useEldColors();
  const totalDays = days?.length ?? 1;
  const nav = useLogbookNavigation(totalDays);
  const currentDay = days ? days[nav.activeDay] : day;

  const exportPdf = useCallback(async () => {
    const canvas = canvasRef.current;
    if (!canvas) return;

    const { default: jsPDF } = await import('jspdf');
    const imgData = canvas.toDataURL('image/png');
    const pdf = new jsPDF({ orientation: 'portrait', unit: 'px', format: [CANVAS_WIDTH, CANVAS_HEIGHT] });
    pdf.addImage(imgData, 'PNG', 0, 0, CANVAS_WIDTH, CANVAS_HEIGHT);
    pdf.save(`logbook-day-${currentDay?.day ?? 0 + 1}.pdf`);
  }, [currentDay]);

  useImperativeHandle(ref, () => ({ exportPdf }), [exportPdf]);

  useEffect(() => {
    const canvas = canvasRef.current;
    if (!canvas || !currentDay) return;
    const ctx = canvas.getContext('2d');
    if (!ctx) return;

    const dpr = window.devicePixelRatio || 1;
    canvas.width = CANVAS_WIDTH * dpr;
    canvas.height = CANVAS_HEIGHT * dpr;
    canvas.style.width = `${CANVAS_WIDTH}px`;
    canvas.style.height = `${CANVAS_HEIGHT}px`;
    ctx.scale(dpr, dpr);

    renderCanvas(ctx, currentDay, eldColors, cycleSchedule, cycleMaxHours, tractorNumber, trailerNumber, shipperName);
  }, [currentDay, eldColors, cycleSchedule, cycleMaxHours, tractorNumber, trailerNumber, shipperName]);

  if (!currentDay) return null;

  return (
    <Box aria-label="ELD logbook sheet">
      {days && days.length > 1 && (
        <Stack direction="row" alignItems="center" spacing={1} sx={{ mb: 1.5 }}>
          <IconButton size="small" onClick={nav.prevDay} disabled={!nav.hasPrev} aria-label="Previous day">
            <ChevronLeft fontSize="small" />
          </IconButton>
          <Tabs
            value={nav.activeDay}
            onChange={(_, v) => nav.setActiveDay(v)}
            variant="scrollable"
            scrollButtons={false}
            sx={{ minHeight: 32, '& .MuiTab-root': { minHeight: 32, py: 0, textTransform: 'none', fontWeight: 600, fontSize: 13 } }}
          >
            {days.map((d) => (
              <Tab key={d.day} label={`Day ${d.day}`} />
            ))}
          </Tabs>
          <IconButton size="small" onClick={nav.nextDay} disabled={!nav.hasNext} aria-label="Next day">
            <ChevronRight fontSize="small" />
          </IconButton>
        </Stack>
      )}

      <Box
        sx={{
          position: 'relative',
          maxWidth: CANVAS_WIDTH,
          mx: 'auto',
          bgcolor: '#ffffff',
          borderRadius: 1,
          overflow: 'hidden',
          border: '1px solid #cccccc',
          '@media print': {
            border: 'none',
            borderRadius: 0,
            maxWidth: '100%',
            '& canvas': { width: '100% !important', height: 'auto !important' },
          },
        }}
      >
        <canvas
          ref={canvasRef}
          style={{
            width: '100%',
            height: 'auto',
            display: 'block',
          }}
          aria-label={`Log sheet for day ${currentDay.day}: ${currentDay.date}, from ${currentDay.from_location} to ${currentDay.to_location}`}
        />
      </Box>

    </Box>
  );
});
