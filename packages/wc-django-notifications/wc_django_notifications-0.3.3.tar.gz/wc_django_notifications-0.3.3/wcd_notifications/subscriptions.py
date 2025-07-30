from django.dispatch import receiver

from .signals import (
    notifications_sent, notifications_updated, notifications_cleared,
)
from .services import manager


@receiver(notifications_sent)
@receiver(notifications_updated)
@receiver(notifications_cleared)
def update_stats_on_notifications_change(sender, instances, **kw):
    recipients = {x.recipient for x in instances} - {None}

    if len(recipients) > 0:
        manager.collect_stats(recipients)
