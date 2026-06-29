import { z } from "zod";

export const tripSchema = z.object({
  currentLocation: z.string().min(2, "Location required").max(500),
  pickupLocation: z.string().min(2, "Location required").max(500),
  dropoffLocation: z.string().min(2, "Location required").max(500),
  cycleHoursUsed: z.number().min(0, "Cannot be negative").max(70, "Exceeds cycle limit"),
  cycleSchedule: z.enum(["60", "70"]).default("70"),
  tripDate: z.union([z.string().date(), z.literal('')]).optional(),
  tractorNumber: z.string().max(50).optional().default(""),
  trailerNumber: z.string().max(50).optional().default(""),
  shipperName: z.string().max(255).optional().default(""),
});

export type TripFormValues = z.infer<typeof tripSchema>;
