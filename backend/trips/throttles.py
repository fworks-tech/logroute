from rest_framework.throttling import AnonRateThrottle


class PlanRouteThrottle(AnonRateThrottle):
    """Throttle for the plan-route endpoint: 100 requests per hour."""

    scope = "plan_route"
    rate = "100/hour"


class AuthThrottle(AnonRateThrottle):
    """Throttle for auth endpoints (login, register): 20 requests per hour."""

    scope = "auth"
    rate = "20/hour"
