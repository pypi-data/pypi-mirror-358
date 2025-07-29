from django.apps import AppConfig as DjangoAppConfig


class AppConfig(DjangoAppConfig):
    name = "protocol_app"
    verbose_name = "Protocol Incident"
