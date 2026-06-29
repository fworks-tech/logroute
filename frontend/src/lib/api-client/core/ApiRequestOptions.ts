export type ApiRequestOptions = {
  method: string;
  url: string;
  path?: Record<string, any>;
  query?: Record<string, any>;
  headers?: Record<string, any>;
  body?: any;
  mediaType?: string;
  responseHeader?: string;
  errors?: Record<number, string>;
};
