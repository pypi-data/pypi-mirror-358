from django.apps import AppConfig
from django.utils.translation import pgettext_lazy


__all__ = ('NotificationsConfig',)


class NotificationsConfig(AppConfig):
    name = 'wcd_notifications'
    verbose_name = pgettext_lazy('wcd_notifications', 'Notifications')
    default_auto_field = 'django.db.models.BigAutoField'

    def ready(self) -> None:
        super().ready()

        from . import subscriptions
