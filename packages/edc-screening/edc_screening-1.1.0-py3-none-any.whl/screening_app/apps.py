from django.apps import AppConfig as DjangoAppConfig


class AppConfig(DjangoAppConfig):
    name = "screening_app"
    verbose_name = "Edc Screening test app"
