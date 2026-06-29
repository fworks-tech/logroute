import React, { useState } from 'react';
import Accordion from '@mui/material/Accordion';
import AccordionSummary from '@mui/material/AccordionSummary';
import AccordionDetails from '@mui/material/AccordionDetails';
import Box from '@mui/material/Box';
import Typography from '@mui/material/Typography';
import ExpandMoreIcon from '@mui/icons-material/ExpandMore';
import { StatusChip } from '@/components/atoms/StatusChip';
import type { LogbookDay } from '@/types/trip';

/** Props for the LogbookDayDetail component. */
export interface LogbookDayDetailProps { days: LogbookDay[]; }

/** Renders an accordion list of logbook days with expandable event tables. */
export const LogbookDayDetail: React.FC<LogbookDayDetailProps> = ({ days }) => {
  const [expanded, setExpanded] = useState<number | false>(false);
  const toggle = (day: number) => (_: React.SyntheticEvent, isExpanded: boolean) => { setExpanded(isExpanded ? day : false); };

  return (
    <Box>
      {days.map((day) => (
        <Accordion key={day.day} expanded={expanded === day.day} onChange={toggle(day.day)} disableGutters elevation={0} sx={{ '&:not(:last-child)': { mb: 1 }, borderRadius: 1, bgcolor: 'transparent' }}>
          <AccordionSummary expandIcon={<ExpandMoreIcon sx={{ color: '#64748b' }} />} aria-controls={`logbook-day-${day.day + 1}-content`} id={`logbook-day-${day.day + 1}-header`}>
            <Box sx={{ display: 'flex', alignItems: 'center', gap: 2, flexWrap: 'wrap' }}>
              <Typography variant="subtitle2" sx={{ fontWeight: 700, color: '#0f172a' }}>Day {day.day + 1} — {day.date}</Typography>
              <Typography variant="caption" sx={{ color: '#64748b' }}>{day.from_location} → {day.to_location}</Typography>
              <Typography variant="caption" sx={{ color: '#64748b' }}>{day.daily_miles.toFixed(0)} mi · {day.total_driving_hours.toFixed(1)} hrs driving</Typography>
            </Box>
          </AccordionSummary>
          <AccordionDetails sx={{ p: 0 }}>
            <Box component="table" sx={{ width: '100%', borderCollapse: 'collapse', fontSize: '0.8rem' }} role="table" aria-label={`Log events for day ${day.day + 1}`}>
              <Box component="thead">
                <Box component="tr" sx={{ bgcolor: '#f1f5f9' }}>
                  {['Time', 'Status', 'Duration', 'Location'].map((h) => (
                    <Box key={h} component="th" sx={{ p: '6px 12px', textAlign: 'left', fontWeight: 600, color: '#475569', fontSize: '0.75rem' }}>{h}</Box>
                  ))}
                </Box>
              </Box>
              <Box component="tbody">
                {day.events.map((event, i) => (
                  <Box key={i} component="tr" sx={{ '&:not(:last-child) td': { borderBottom: '1px solid #e2e8f0' } }}>
                    <Box component="td" sx={{ p: '6px 12px', whiteSpace: 'nowrap', color: '#64748b' }}>{event.start_time}–{event.end_time}</Box>
                    <Box component="td" sx={{ p: '6px 12px' }}><StatusChip status={event.status} /></Box>
                    <Box component="td" sx={{ p: '6px 12px', whiteSpace: 'nowrap', color: '#0f172a' }}>{event.duration_hours.toFixed(2)} hrs</Box>
                    <Box component="td" sx={{ p: '6px 12px', color: '#64748b' }}>{event.label ?? event.location ?? '—'}</Box>
                  </Box>
                ))}
              </Box>
            </Box>
          </AccordionDetails>
        </Accordion>
      ))}
    </Box>
  );
};
