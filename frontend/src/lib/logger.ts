/** Supported log severity levels. */
export type LogLevel = 'debug' | 'info' | 'warn' | 'error';

/** A structured log entry with timestamp, level, correlation ID, and optional error/data. */
export interface LogEntry {
  timestamp: string;
  level: LogLevel;
  correlationId: string;
  message: string;
  data?: Record<string, any>;
  error?: { message: string; stack?: string };
}

/** Generates a unique correlation ID from timestamp and random characters. */
export function generateCorrelationId(): string {
  return `${Date.now()}-${Math.random().toString(36).substring(2, 11)}`;
}

/** Structured logger with correlation tracking, environment-aware output, and PII-safe formatting. */
export class Logger {
  private correlationId: string;
  private isDevelopment: boolean;

  constructor(correlationId?: string, isDevelopment: boolean = import.meta.env.DEV) {
    this.correlationId = correlationId || generateCorrelationId();
    this.isDevelopment = isDevelopment;
  }

  getCorrelationId(): string { return this.correlationId; }
  setCorrelationId(id: string): void { this.correlationId = id; }
  debug(message: string, data?: Record<string, any>): void { if (this.isDevelopment) this.log('debug', message, data); }
  info(message: string, data?: Record<string, any>): void { this.log('info', message, data); }
  warn(message: string, data?: Record<string, any>): void { this.log('warn', message, data); }
  error(message: string, error?: Error | string, data?: Record<string, any>): void {
    const errorObj = typeof error === 'string' ? new Error(error) : error;
    this.log('error', message, data, errorObj);
  }

  private log(level: LogLevel, message: string, data?: Record<string, any>, error?: Error): void {
    const entry: LogEntry = {
      timestamp: new Date().toISOString(),
      level,
      correlationId: this.correlationId,
      message,
      data: data ? { ...data } : undefined,
      error: error ? { message: error.message, stack: this.isDevelopment ? error.stack : undefined } : undefined,
    };
    if (this.isDevelopment) {
      const styles = { debug: 'color: #888', info: 'color: #f59e0b; font-weight: bold', warn: 'color: #ff8800; font-weight: bold', error: 'color: #ef4444; font-weight: bold' };
      console.log(`%c[${entry.level.toUpperCase()}] ${entry.correlationId}`, styles[entry.level], entry.message);
      if (entry.data) console.log('  Data:', entry.data);
      if (entry.error) console.log('  Error:', entry.error.message);
    } else {
      if (entry.level === 'debug' || entry.level === 'info') return;
      const json = JSON.stringify(entry);
      if (entry.level === 'error') console.error(json);
      else if (entry.level === 'warn') console.warn(json);
    }
  }
}

/** Default singleton logger instance. */
export const logger = new Logger();
