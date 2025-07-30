from kid_sdk.kid_profile.models import DomesticProfile, InternationalProfile


__all__ = [
    "UserProfileMixin",
]


class UserProfileMixin:
    @property
    def profile(self):
        if not hasattr(self, "_profile"):
            self._profile = self._get_profile()
        return self._profile

    def _get_profile(self):
        try:
            return DomesticProfile.objects.using("domestic").get(smart_id=self.smart_id)
        except DomesticProfile.DoesNotExist:
            try:
                return InternationalProfile.objects.using("international").get(smart_id=self.smart_id)
            except InternationalProfile.DoesNotExist:
                return None

    @property
    def first_name(self):
        return self.profile.first_name if self.profile else None

    @property
    def last_name(self):
        return self.profile.last_name if self.profile else None

    @property
    def phone(self):
        return self.profile.phone if self.profile else None

    @property
    def email(self):
        return self.profile.email if self.profile else None

    @property
    def user_type(self):
        if not self.profile:
            return "unknown"
        return "domestic" if isinstance(self.profile, DomesticProfile) else "international"
