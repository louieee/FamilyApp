from django.apps import AppConfig


class CoreConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "core"

    def ready(self):
        import core.signals.timetable  # noqa
        import core.signals.scheduler # noqa
        import core.signals.subscription # noqa