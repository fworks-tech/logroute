import React from 'react';
import { motion } from 'motion/react';
import Card from '@mui/material/Card';
import CardContent from '@mui/material/CardContent';
import Typography from '@mui/material/Typography';
import Box from '@mui/material/Box';

/** Props for the StatCard component. */
export interface StatCardProps {
  icon: React.ReactNode;
  label: string;
  value: string | number;
  unit?: string;
  delay?: number;
}

const MotionCard = motion.create(Card);

/** Animated card displaying a single statistic with icon, label, and value. */
export const StatCard: React.FC<StatCardProps> = ({ icon, label, value, unit, delay = 0 }) => (
  <MotionCard
    initial={{ opacity: 0, y: 20 }}
    animate={{ opacity: 1, y: 0 }}
    transition={{ duration: 0.4, delay }}
    whileHover={{ y: -2 }}
    sx={{ height: '100%' }}
  >
    <CardContent sx={{ textAlign: 'center', py: 3 }}>
      <Box sx={{ color: '#0D3B4E', mb: 1, '& svg': { fontSize: 32 } }} aria-hidden="true">
        {icon}
      </Box>
      <Typography variant="h5" sx={{ fontWeight: 700, color: '#0f172a' }}>
        {value}
        {unit && <Typography component="span" variant="body2" sx={{ color: '#64748b', ml: 0.5 }}>{unit}</Typography>}
      </Typography>
      <Typography variant="caption" sx={{ color: '#64748b', mt: 0.5, display: 'block' }}>
        {label}
      </Typography>
    </CardContent>
  </MotionCard>
);
