from datetime import datetime
from typing import List, Optional, Sequence
from px_pipeline import StraightPipeline

from django.db import models
from django.utils import timezone

from ..models import Notification
from ..signals import notification_sent, notifications_sent
from ..conf import settings


def send(
    message: str,
    recipients: Sequence[models.Model],
    actor: Optional[models.Model] = None,
    action: Optional[models.Model] = None,
    target: Optional[models.Model] = None,
    parent: Optional[Notification] = None,
    flags: List[int] = [],
    extra: dict = {},
    send_at: Optional[datetime] = None,
    now: Optional[datetime] = None,
    batch_size: Optional[int] = None,
) -> List[Notification]:
    assert len(recipients) > 0, 'Must have at least one recipient.'

    actual_now = timezone.now()
    now = actual_now if now is None else now
    send_at = now if send_at is None else send_at

    notifications = []

    for recipient in recipients:
        notification = Notification(
            message=message.format(
                recipient=recipient, actor=actor, action=action, target=target,
                flags=flags, extra=extra, now=now, actual_now=actual_now,
            ),
            recipient=recipient, actor=actor, action=action, target=target,
            parent=parent, flags=flags, created_at=now, sent_at=send_at,
            data={'actual_now': actual_now.isoformat(), **extra},
        )
        notification.recipient = recipient
        notification.actor = actor
        notification.action = action
        notification.target = target
        notification.prepare()
        notifications.append(notification)

    prepared = StraightPipeline(settings.PREPARATION_PIPELINE)({
        'instances': notifications,
    })
    notifications = Notification.objects.bulk_create(
        prepared['instances'], batch_size=batch_size,
    )

    for notification in notifications:
        notification_sent.send(Notification, instance=notification)

    notifications_sent.send(Notification, instances=notifications)

    return notifications
