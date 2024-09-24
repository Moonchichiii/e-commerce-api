from rest_framework.throttling import UserRateThrottle

class LoginRateThrottle(UserRateThrottle):
    rate = '3/minute'

class AdminRateThrottle(UserRateThrottle):
    rate = '100/minute'

class RegularUserRateThrottle(UserRateThrottle):
    rate = '10/minute'