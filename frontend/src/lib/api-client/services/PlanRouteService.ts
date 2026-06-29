import type { TripInput } from '../models/TripInput';
import type { TripOutput } from '../models/TripOutput';
import type { CancelablePromise } from '../core/CancelablePromise';
import { OpenAPI } from '../core/OpenAPI';
import { request as __request } from '../core/request';

export class PlanRouteService {
  public static planRouteCreate(requestBody: TripInput): CancelablePromise<TripOutput> {
    return __request(OpenAPI, {
      method: 'POST',
      url: '/api/plan-route/',
      body: requestBody,
      mediaType: 'application/json',
    });
  }
}
