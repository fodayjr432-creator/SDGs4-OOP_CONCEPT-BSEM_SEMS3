from django.conf import settings
from django.db import models
from django.db.models.functions import Lower


class Institution(models.Model):
    name = models.CharField(max_length=255)
    is_singleton = models.BooleanField(default=True, unique=True, editable=False)

    class Meta:
        db_table = "accounts_institution"
        verbose_name = "institution"
        verbose_name_plural = "institutions"

    def __str__(self):
        return self.name


class UserProfile(models.Model):
    class Role(models.TextChoices):
        INSTITUTION_ADMIN = "institution_admin", "Institution administrator"
        STAFF = "staff", "Staff"

    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="account_profile",
    )
    institution = models.ForeignKey(
        Institution,
        on_delete=models.PROTECT,
        related_name="user_profiles",
    )
    administrator_name = models.CharField(max_length=255)
    email = models.EmailField(max_length=254)
    role = models.CharField(max_length=32, choices=Role.choices)

    class Meta:
        db_table = "accounts_userprofile"
        constraints = [
            models.UniqueConstraint(
                Lower("email"),
                name="accounts_userprofile_email_ci_unique",
            )
        ]

    def __str__(self):
        return f"{self.administrator_name} ({self.user.username})"
