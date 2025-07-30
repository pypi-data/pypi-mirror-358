from django.db import models
from django.core.exceptions import FieldError

from kid_sdk.kid_profile.models import DomesticProfile, InternationalProfile


__all__ = [
    "ProfileManager",
]


class ProfileQuerySetException(Exception):
    pass


class ProfileQuerySet(models.query.QuerySet):
    FIELDS = ["first_name", "last_name", "phone", "email"]

    def _filter_domestic_ids(self, *args, filters: dict) -> list:
        q = models.Q()
        for field, value in filters.items():
            if field.split("__")[0] in self.FIELDS:
                q &= models.Q(**{field: value})
        return list(DomesticProfile.objects.using("domestic").filter(*args, q).values_list("smart_id", flat=True))

    def _filter_international_ids(self, *args, filters: dict) -> list:
        q = models.Q()
        for field, value in filters.items():
            if field.split("__")[0] in self.FIELDS:
                q &= models.Q(**{field: value})
        return list(
            InternationalProfile.objects.using("international").filter(*args, q).values_list("smart_id", flat=True)
        )

    def filter(self, *args, **filters):
        try:
            domestic_ids = self._filter_domestic_ids(*args, filters=filters)
            international_ids = self._filter_international_ids(*args, filters=filters)
        except FieldError:
            if args:
                allowed_fields = ", ".join(["smart_id"] + self.FIELDS)
                raise ProfileQuerySetException(
                    f"Использование Q функций разрешено только с полями из моделей Profile: {allowed_fields}"
                )
            raise

        all_ids = list(set(domestic_ids) | set(international_ids))
        local_filters = {k: v for k, v in filters.items() if k.split("__")[0] not in self.FIELDS}
        return super().filter(**local_filters, smart_id__in=all_ids)


class ProfileManager(models.Manager):
    def get_queryset(self):
        return ProfileQuerySet(self.model, using=self._db)

    def all(self):
        return ProfileQuerySet(self.model, using=self._db).all()
