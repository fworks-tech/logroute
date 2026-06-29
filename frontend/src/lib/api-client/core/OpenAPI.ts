export type OpenAPIConfig = {
  BASE: string;
  VERSION: string;
  WITH_CREDENTIALS: boolean;
  CREDENTIALS: 'include' | 'omit' | 'same-origin';
  TOKEN?: string | (() => string | undefined);
  USERNAME?: string | (() => string | undefined);
  PASSWORD?: string | (() => string | undefined);
  HEADERS?: Record<string, any> | (() => Record<string, any>);
  ENCODE_PATH?: (path: string) => string;
};

export const OpenAPI: OpenAPIConfig = {
  BASE: 'http://localhost:8000',
  VERSION: '1.0.0',
  WITH_CREDENTIALS: false,
  CREDENTIALS: 'include',
};
