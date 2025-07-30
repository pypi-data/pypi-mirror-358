from typing import *
from dataclasses import dataclass

from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.utils.translation import pgettext_lazy
from django.db import models
from django.contrib.postgres.indexes import BTreeIndex

from ..utils import (
    make_generic_Q, ModelDef, group_and_sort, resolve_generic_field_data
)


__all__ = 'StatsQuerySet', 'Stats', 'TOTAL_FLAG',

TOTAL_FLAG = 0


# FIXME: This is a fallback model for an old behaviour
@dataclass
class StatsTotal:
    flags: Dict[int, int]

    recipient_content_type_id: Optional[int]
    recipient_content_type: Optional[models.Model]
    recipient_object_id: Optional[str]
    recipient: Optional[models.Model]
    total: Optional[int]


class StatsQuerySet(models.QuerySet):
    def recipients(self, recipients: Sequence[ModelDef]):
        return self.filter(make_generic_Q('recipient', recipients))

    def resolve_total_flags(self):
        items = group_and_sort(self, key=lambda item: (
            item.recipient_content_type_id, item.recipient_object_id
        ))
        result = []

        for _, stats in items:
            # FIXME: This recipient getter is ugly:
            stats = list(stats)
            recipient_content_type, recipient_object_id, recipient = (
                resolve_generic_field_data(stats[0], 'recipient')
            )

            flags = {
                flag: sum(x.amount for x in items)
                for flag, items in group_and_sort(
                    stats, key=lambda item: item.flag
                )
            }
            total = flags.pop(TOTAL_FLAG, None)
            result.append(StatsTotal(
                flags, total=total,
                recipient_content_type_id=getattr(recipient_content_type, 'pk', None),
                recipient_content_type=recipient_content_type,
                recipient_object_id=recipient_object_id,
                recipient=recipient,
            ))

        return result


class Stats(models.Model):
    objects = StatsQuerySet.as_manager()

    class Meta:
        verbose_name = pgettext_lazy('wcd_notifications', 'Notification stats')
        verbose_name_plural = pgettext_lazy(
            'wcd_notifications', 'List of notifications stats'
        )
        ordering = ('-pk',)
        indexes = [
            BTreeIndex(fields=['recipient_content_type', 'recipient_object_id']),
        ]

    recipient_content_type = models.ForeignKey(
        ContentType,
        verbose_name=pgettext_lazy('wcd_notifications', 'Recipient: Content type'),
        related_name='stats_recipient', on_delete=models.CASCADE,
    )
    recipient_object_id = models.CharField(
        verbose_name=pgettext_lazy('wcd_notifications', 'Recipient: Id'),
        max_length=255, null=False, blank=False,
    )
    recipient = GenericForeignKey('recipient_content_type', 'recipient_object_id')

    actor_content_type = models.ForeignKey(
        ContentType, null=True, blank=True,
        verbose_name=pgettext_lazy('wcd_notifications', 'Actor: Content type'),
        related_name='notification_stats_actor', on_delete=models.SET_NULL,
    )
    action_content_type = models.ForeignKey(
        ContentType, null=True, blank=True,
        verbose_name=pgettext_lazy('wcd_notifications', 'Action: Content type'),
        related_name='notification_stats_action', on_delete=models.SET_NULL,
    )
    target_content_type = models.ForeignKey(
        ContentType, null=True, blank=True,
        verbose_name=pgettext_lazy('wcd_notifications', 'Target: Content type'),
        related_name='notification_stats_target', on_delete=models.SET_NULL,
    )

    flag = models.BigIntegerField(
        verbose_name=pgettext_lazy('wcd_notifications', 'Flag'),
        default=0,
    )
    amount = models.BigIntegerField(
        verbose_name=pgettext_lazy('wcd_notifications', 'Amount'),
        default=0,
    )

    def __str__(self):
        return str(self.pk)
