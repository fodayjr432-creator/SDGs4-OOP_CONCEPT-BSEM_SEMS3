from datetime import timedelta

from django.utils import timezone
from rest_framework.authentication import TokenAuthentication
from rest_framework.exceptions import AuthenticationFailed


TOKEN_MAX_AGE = timedelta(hours=12)


class InstitutionTokenAuthentication(TokenAuthentication):
    def authenticate_credentials(self, key):
        token = self._get_token(key)
        if timezone.now() - token.created > TOKEN_MAX_AGE:
            token.delete()
            raise AuthenticationFailed("Token expired.")
        if not token.user.is_active:
            raise AuthenticationFailed("User account is inactive.")
        return token.user, token

    @staticmethod
    def _get_token(key):
        from rest_framework.authtoken.models import Token

        try:
            return Token.objects.select_related("user").get(key=key)
        except Token.DoesNotExist as error:
            raise AuthenticationFailed("Invalid token.") from error
