/** Redacts personally identifiable information (locations, coordinates, keys, phone, email) from a string. */
export function redactPII(text: string | unknown): string {
  if (!text || typeof text !== 'string') return String(text);
  let redacted = text;
  redacted = redacted.replace(/[A-Z][a-z]+,\s*[A-Z]{2}(?:\s+\d{5})?/g, '[LOCATION]');
  redacted = redacted.replace(/-?\d+\.\d{4,}/g, '[COORDINATE]');
  redacted = redacted.replace(/(api[_-]?key|token|secret|password)[\s=:]*([^\s,}]+)/gi, '$1=[REDACTED]');
  redacted = redacted.replace(/\d{3}[-.\s]?\d{3}[-.\s]?\d{4}/g, '[PHONE]');
  redacted = redacted.replace(/\b[A-Z0-9._%+-]+@[A-Z0-9.-]+\.[A-Z]{2,}\b/gi, '[EMAIL]');
  return redacted;
}

const DEFAULT_SENSITIVE_FIELDS = ['location', 'address', 'city', 'state', 'zipcode', 'zip', 'latitude', 'lat', 'longitude', 'lon', 'coordinates', 'phone', 'email', 'apikey', 'api_key', 'token', 'secret', 'password'];

/** Recursively redacts sensitive fields and PII from an object tree. */
export function redactObject(obj: unknown, sensitiveFields: string[] = DEFAULT_SENSITIVE_FIELDS): unknown {
  if (obj === null || obj === undefined) return obj;
  if (typeof obj === 'string') return redactPII(obj);
  if (typeof obj !== 'object') return obj;
  if (Array.isArray(obj)) return obj.map(item => redactObject(item, sensitiveFields));
  const redacted: Record<string, any> = {};
  for (const [key, value] of Object.entries(obj)) {
    const lowerKey = key.toLowerCase();
    if (sensitiveFields.some(field => lowerKey.includes(field))) {
      redacted[key] = typeof value === 'string' ? '[REDACTED]' : value === null ? null : '[REDACTED]';
    } else if (typeof value === 'string') {
      redacted[key] = redactPII(value);
    } else if (typeof value === 'object') {
      redacted[key] = redactObject(value, sensitiveFields);
    } else {
      redacted[key] = value;
    }
  }
  return redacted;
}

/** Redacts PII from an Error object, string, or unknown value and returns a safe string representation. */
export function redactError(error: Error | string | unknown): string {
  if (error instanceof Error) {
    const message = redactPII(error.message);
    const stack = error.stack ? redactPII(error.stack) : undefined;
    return `${error.constructor.name}: ${message}${stack ? `\n${stack}` : ''}`;
  }
  if (typeof error === 'string') return redactPII(error);
  return String(error);
}
