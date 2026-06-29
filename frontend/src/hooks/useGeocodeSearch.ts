import { useState, useCallback, useRef } from 'react';
import axios from 'axios';

/** Result from the geocoding API with display name and coordinates. */
export interface GeocodeResult {
  display_name: string;
  lat: number;
  lon: number;
  osm_id: number;
}

/** Return type for the useGeocodeSearch hook. */
export interface UseGeocodeSearchReturn {
  inputValue: string;
  setInputValue: (value: string) => void;
  suggestions: GeocodeResult[];
  isLoading: boolean;
  error: string | null;
  search: (query: string) => void;
}

const GEOCODE_URL = '/api/geocode/';
const SEARCH_DEBOUNCE_MS = 300;
const MIN_QUERY_LENGTH = 2;

/** Hook that provides debounced geocoding search with suggestions, loading, and error state. */
export function useGeocodeSearch(): UseGeocodeSearchReturn {
  const [inputValue, setInputValue] = useState('');
  const [suggestions, setSuggestions] = useState<GeocodeResult[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const debounceTimerRef = useRef<NodeJS.Timeout | undefined>(undefined);

  const search = useCallback((query: string) => {
    if (debounceTimerRef.current) {
      clearTimeout(debounceTimerRef.current as NodeJS.Timeout);
    }

    if (!query || query.length < MIN_QUERY_LENGTH) {
      setSuggestions([]);
      setError(null);
      return;
    }

    debounceTimerRef.current = setTimeout(async () => {
      setIsLoading(true);
      setError(null);

      try {
        const response = await axios.get<GeocodeResult[]>(GEOCODE_URL, {
          params: { q: query },
          timeout: 5000,
        });
        setSuggestions(response.data);
        if (response.data.length === 0) {
          setError('No locations found. Try a different search.');
        }
      } catch (err) {
        const message = axios.isAxiosError(err)
          ? err.response?.status === 429
            ? 'Too many requests. Please wait a moment.'
            : 'Failed to search locations. Please try again.'
          : 'Failed to search locations. Check your connection.';
        setError(message);
        setSuggestions([]);
      } finally {
        setIsLoading(false);
      }
    }, SEARCH_DEBOUNCE_MS);
  }, []);

  return { inputValue, setInputValue, suggestions, isLoading, error, search };
}
