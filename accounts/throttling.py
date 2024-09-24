from rest_framework.throttling import AnonRateThrottle, UserRateThrottle

class IPBasedAnonRateThrottle(AnonRateThrottle):
    rate = '100/day'

class IPBasedUserRateThrottle(UserRateThrottle):
    rate = '1000/day'

class LoginRateThrottle(UserRateThrottle):
    rate = '3/minute'

