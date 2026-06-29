import React from 'react';
import Paper from '@mui/material/Paper';
import Typography from '@mui/material/Typography';
import Divider from '@mui/material/Divider';
import Box from '@mui/material/Box';

export interface SectionPaperProps {
  title: string;
  subtitle?: string;
  icon?: React.ReactNode;
  children: React.ReactNode;
}

export const SectionPaper: React.FC<SectionPaperProps> = ({ title, subtitle, icon, children }) => {
  const headingId = `section-${title.toLowerCase().replace(/\s+/g, '-')}`;

  return (
    <Paper component="section" aria-labelledby={headingId} elevation={0} sx={{ p: { xs: 2, md: 3 }, mb: 3 }}>
      <Box sx={{ display: 'flex', alignItems: 'center', gap: 1, mb: 1 }}>
        {icon && <Box sx={{ color: '#0D3B4E', display: 'flex' }}>{icon}</Box>}
        <Box>
          <Typography id={headingId} variant="h6" sx={{ fontWeight: 600, color: '#0f172a' }}>
            {title}
          </Typography>
          {subtitle && <Typography variant="caption" sx={{ color: '#64748b' }}>{subtitle}</Typography>}
        </Box>
      </Box>
      <Divider sx={{ mb: 2 }} />
      {children}
    </Paper>
  );
};
