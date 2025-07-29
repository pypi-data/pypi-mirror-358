from django.conf import settings as django_settings


class Settings:
    @property
    def DATA_PURGERS(self) -> list[str]:
        return getattr(
            django_settings,
            "DATA_PURGERS",
            [],
        )


settings = Settings()
