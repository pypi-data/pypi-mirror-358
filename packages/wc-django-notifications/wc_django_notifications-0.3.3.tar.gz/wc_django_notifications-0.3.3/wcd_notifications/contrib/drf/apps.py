from django.apps import AppConfig
from django.utils.translation import pgettext_lazy


__all__ = ('DRFConfig',)


class DRFConfig(AppConfig):
    name = 'wcd_notifications.contrib.drf'
    label = 'wcd_notifications_drf'
    verbose_name = pgettext_lazy('wcd_notifications', 'Notifications DRF')
    default_auto_field = 'django.db.models.BigAutoField'
