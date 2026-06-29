from rest_framework.throttling import AnonRateThrottle


class PlanRouteThrottle(AnonRateThrottle):
    scope = "plan_route"
    rate = "100/hour"


class AuthThrottle(AnonRateThrottle):
    scope = "auth"
    rate = "20/hour"
