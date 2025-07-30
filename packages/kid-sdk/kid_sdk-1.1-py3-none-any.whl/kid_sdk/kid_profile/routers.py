from django.contrib.auth import get_user_model


class ProfileRouter:
    def db_for_read(self, model, **hints):
        if model.__name__ in ["DomesticProfile", "InternationalProfile"]:
            return model.__name__.lower().replace("profile", "")
        return None

    def db_for_write(self, model, **hints):
        if model.__name__ in ["DomesticProfile", "InternationalProfile"]:
            return model.__name__.lower().replace("profile", "")
        return None

    def allow_relation(self, obj1, obj2, **hints):
        User = get_user_model()
        if isinstance(obj1, User) or isinstance(obj2, User):
            return True
        return None

    def allow_migrate(self, db, app_label, model_name=None, **hints):
        if model_name in ["domesticprofile", "internationalprofile"]:
            return db == model_name.replace("profile", "")
        return None


class ReadOnlyProfileRouter(ProfileRouter):
    def db_for_write(self, model, **hints):
        if model.__name__ in ["DomesticProfile", "InternationalProfile"]:
            return False
        return None

    def allow_migrate(self, db, app_label, model_name=None, **hints):
        if model_name in ["domesticprofile", "internationalprofile"]:
            return False
        return None
