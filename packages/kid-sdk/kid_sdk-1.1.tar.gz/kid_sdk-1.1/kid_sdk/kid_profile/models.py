from django.db import models


__all__ = [
    "DomesticProfile",
    "InternationalProfile",
]


class Profile(models.Model):
    smart_id = models.UUIDField(unique=True, db_index=True, primary_key=True, max_length=128)
    first_name = models.CharField(verbose_name="Имя", max_length=128)
    last_name = models.CharField(verbose_name="Фамилия", max_length=128)
    email = models.EmailField(unique=True, verbose_name="E-mail", max_length=128)
    phone = models.CharField(unique=True, verbose_name="Телефон", max_length=128)

    class Meta:
        abstract = True


class DomesticProfile(Profile):
    class Meta:
        ordering = ["smart_id"]


class InternationalProfile(Profile):
    class Meta:
        ordering = ["smart_id"]
