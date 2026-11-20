from rest_framework.throttling import SimpleRateThrottle


class IpRateThrottle(SimpleRateThrottle):
    def get_cache_key(self, request, view):
        return self.cache_format % {
            "scope": self.scope,
            "ident": self.get_ident(request),
        }


class LoginRateThrottle(IpRateThrottle):
    scope = "login"


class RegistrationRateThrottle(IpRateThrottle):
    scope = "registration"
