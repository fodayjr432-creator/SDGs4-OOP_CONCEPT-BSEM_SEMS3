from django.core.exceptions import ValidationError


class PasswordComplexityValidator:
    def validate(self, password, user=None):
        if not any(character.isalpha() for character in password):
            raise ValidationError(
                "Password must contain at least one letter.",
                code="password_no_letter",
            )
        if not any(character.isdigit() for character in password):
            raise ValidationError(
                "Password must contain at least one number.",
                code="password_no_number",
            )
        if not any(not character.isalnum() for character in password):
            raise ValidationError(
                "Password must contain at least one special character.",
                code="password_no_special_character",
            )

    def get_help_text(self):
        return (
            "Your password must contain at least one letter, one number, "
            "and one special character."
        )
