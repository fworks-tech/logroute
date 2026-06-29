// @ts-nocheck
import type { OpenAPIConfig } from './OpenAPI';
import type { ApiRequestOptions } from './ApiRequestOptions';
import type { ApiResult } from './ApiResult';
import { ApiError } from './ApiError';
import { CancelablePromise } from './CancelablePromise';
import { redactPII } from '../../redaction';

async function resolve<T>(options: OpenAPIConfig, request: ApiRequestOptions): Promise<T> {
  const url = buildUrl(options, request);
  const headers = buildHeaders(options, request);
  const body = buildBody(request);

  const response = await fetch(url, {
    method: request.method,
    headers,
    body,
    credentials: options.CREDENTIALS,
  });

  const result: ApiResult = {
    url,
    ok: response.ok,
    status: response.status,
    statusText: response.statusText,
    body: await response.json().catch(() => null),
  };

  if (!result.ok) {
    throw new ApiError(request, result, `Request failed: ${result.status} ${result.statusText}`);
  }

  return result.body as T;
}

function buildUrl(options: OpenAPIConfig, request: ApiRequestOptions): string {
  let url = `${options.BASE}${request.url}`;
  if (request.path) {
    for (const [key, value] of Object.entries(request.path)) {
      url = url.replace(`{${key}}`, encodeURIComponent(String(value)));
    }
  }
  if (request.query) {
    const params = new URLSearchParams();
    for (const [key, value] of Object.entries(request.query)) {
      if (value !== undefined && value !== null) {
        params.append(key, String(value));
      }
    }
    const queryString = params.toString();
    if (queryString) {
      url += `?${queryString}`;
    }
  }
  if (options.ENCODE_PATH) {
    url = options.ENCODE_PATH(url);
  }
  return url;
}

function buildHeaders(options: OpenAPIConfig, request: ApiRequestOptions): Record<string, string> {
  const headers: Record<string, string> = {
    'Content-Type': 'application/json',
  };

  if (options.HEADERS) {
    const optionHeaders = typeof options.HEADERS === 'function' ? options.HEADERS() : options.HEADERS;
    Object.assign(headers, optionHeaders);
  }

  if (request.headers) {
    Object.assign(headers, request.headers);
  }

  if (options.TOKEN) {
    const token = typeof options.TOKEN === 'function' ? options.TOKEN() : options.TOKEN;
    if (token) {
      headers['Authorization'] = `Bearer ${token}`;
    }
  }

  if (options.USERNAME && options.PASSWORD) {
    const username = typeof options.USERNAME === 'function' ? options.USERNAME() : options.USERNAME;
    const password = typeof options.PASSWORD === 'function' ? options.PASSWORD() : options.PASSWORD;
    if (username && password) {
      headers['Authorization'] = `Basic ${btoa(`${username}:${password}`)}`;
    }
  }

  return headers;
}

function buildBody(request: ApiRequestOptions): string | undefined {
  if (request.body === undefined) return undefined;
  return JSON.stringify(request.body);
}

export function request<T>(options: OpenAPIConfig, request: ApiRequestOptions): CancelablePromise<T> {
  return new CancelablePromise<T>((resolve, reject, onCancel) => {
    const controller = new AbortController();
    let cancelled = false;

    onCancel(() => {
      cancelled = true;
      controller.abort();
    });

    resolve(
      (async () => {
        if (cancelled) throw new Error('Request cancelled');
        return resolve<T>(options, { ...request });
      })()
    );
  });
}
