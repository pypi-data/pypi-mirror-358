from datetime import datetime
from typing import *
from enum import Enum
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.postgres.fields import ArrayField
from django.contrib.contenttypes.models import ContentType
from django.utils import timezone
from django.utils.translation import pgettext_lazy
from django.db import models
from django.contrib.postgres.indexes import GinIndex, BTreeIndex
from px_pipeline import Filter

from ..utils import (
    Registry, make_generic_Q, to_intarray, ModelDef, content_type_from_id as ctfid
)
from ..compat import IntegerChoices, JSONField


__all__ = (
    'Readability',
    'NotificationQuerySet', 'Notification',
    'make_generic_Q',
    'prepare_ordering',
)
# Phone keyboard:         READ0
READABILITY_BASE_NUMBER = 73230

RecipientDef = Tuple[ContentType, str]


class FlagStats(TypedDict):
    recipient: RecipientDef
    stats: Dict[int, int]


class Readability(IntegerChoices):
    UNREAD = READABILITY_BASE_NUMBER + 2, pgettext_lazy('wcd_notifications', 'Unread')
    READ = READABILITY_BASE_NUMBER + 6, pgettext_lazy('wcd_notifications', 'Read')


class FlagsRegistry(Registry):
    def add(self, choices: Type[Enum]):
        for item in choices:
            assert item.value not in self, (
                f'Value {item.value} already registered as {self[item.value]}, '
                'check your flags for consistency.'
            )
            assert item.value > 9, (
                f'Value {item.value} is reserved for internal use.'
            )

            self[item.value] = item

    register = add


class NotificationQuerySet(models.QuerySet):
    def read(self):
        return self.filter(flags__contains=to_intarray([self.model.Readability.READ]))

    def unread(self):
        return self.filter(flags__contains=to_intarray([self.model.Readability.UNREAD]))

    def recipients(self, recipients: Sequence[ModelDef]):
        return self.filter(make_generic_Q('recipient', recipients))

    def actors(self, actors: Sequence[ModelDef]):
        return self.filter(make_generic_Q('actor', actors))

    def actions(self, actions: Sequence[ModelDef]):
        return self.filter(make_generic_Q('action', actions))

    def targets(self, targets: Sequence[ModelDef]):
        return self.filter(make_generic_Q('target', targets))

    def sent(self, now: Optional[datetime] = None):
        return self.filter(sent_at=now if now is not None else timezone.now())

    def collect_recipients(self):
        fields = 'recipient_content_type', 'recipient_object_id',
        query = (
            self
            .only(*fields)
            .order_by(*fields)
            .distinct(*fields)
            .prefetch_related('recipient')
        )
        return [x.recipient for x in query if x.recipient]

    def collect_total_stats(self) -> Dict[RecipientDef, int]:
        fields = (
            'recipient_content_type', 'recipient_object_id',
            'actor_content_type', 'action_content_type', 'target_content_type',
        )
        records = (
            self
            .values(*fields)
            .order_by()
            .annotate(count=models.Count('pk'))
            .values_list(*fields, 'count')
        )
        return [
            (ctfid(ct), oid, ctfid(actor), ctfid(action), ctfid(target), count)
            for (ct, oid, actor, action, target, count) in records
        ]

    def collect_flag_stats(self) -> List[FlagStats]:
        fields = (
            'recipient_content_type', 'recipient_object_id', 'flag',
            'actor_content_type', 'action_content_type', 'target_content_type',
        )
        records = (
            self
            .annotate(flag=models.Func('flags', function='unnest'))
            .values(*fields)
            .order_by()
            .annotate(count=models.Count('pk'))
            .values_list(*fields, 'count')
        )

        return [
            (ctfid(ct), oid, ctfid(actor), ctfid(action), ctfid(target), fl, count)
            for (ct, oid, fl, actor, action, target, count) in records
        ]


class Notification(models.Model):
    Readability = Readability

    preparator = Filter()
    flags_registry = FlagsRegistry()
    objects: Union[NotificationQuerySet, models.Manager] = NotificationQuerySet.as_manager()

    class Meta:
        verbose_name = pgettext_lazy('wcd_notifications', 'Notification')
        verbose_name_plural = pgettext_lazy('wcd_notifications', 'Notifications')
        ordering = ('-ordering_field', '-sent_at', '-created_at', '-pk',)
        indexes = [
            GinIndex(
                name='wcdnt_%(class)s_flags',
                fields=['flags'], opclasses=('gin__int_ops',)
            ),
            BTreeIndex(fields=['recipient_content_type', 'recipient_object_id']),
            BTreeIndex(fields=['actor_content_type', 'actor_object_id']),
            BTreeIndex(fields=['action_content_type', 'action_object_id']),
            BTreeIndex(fields=['target_content_type', 'target_object_id']),
        ]

    parent = models.ForeignKey(
        'self', null=True, blank=True, on_delete=models.SET_NULL,
        verbose_name=pgettext_lazy('wcd_notifications', 'Parent notification'),
        related_name='children',
    )

    recipient_content_type = models.ForeignKey(
        ContentType,
        verbose_name=pgettext_lazy('wcd_notifications', 'Recipient: Content type'),
        related_name='notification_recipient', on_delete=models.CASCADE,
    )
    recipient_object_id = models.CharField(
        verbose_name=pgettext_lazy('wcd_notifications', 'Recipient: Id'),
        max_length=255, null=False, blank=False,
    )
    recipient = GenericForeignKey('recipient_content_type', 'recipient_object_id')

    actor_content_type = models.ForeignKey(
        ContentType, null=True, blank=True,
        verbose_name=pgettext_lazy('wcd_notifications', 'Actor: Content type'),
        related_name='notification_actor', on_delete=models.SET_NULL,
    )
    actor_object_id = models.CharField(
        verbose_name=pgettext_lazy('wcd_notifications', 'Actor: Id'),
        max_length=255, null=True, blank=True,
    )
    actor = GenericForeignKey('actor_content_type', 'actor_object_id')

    action_content_type = models.ForeignKey(
        ContentType, null=True, blank=True,
        verbose_name=pgettext_lazy('wcd_notifications', 'Action: Content type'),
        related_name='notification_action', on_delete=models.SET_NULL,
    )
    action_object_id = models.CharField(
        verbose_name=pgettext_lazy('wcd_notifications', 'Action: Id'),
        max_length=255, null=True, blank=True,
    )
    action = GenericForeignKey('action_content_type', 'action_object_id')

    target_content_type = models.ForeignKey(
        ContentType, null=True, blank=True,
        verbose_name=pgettext_lazy('wcd_notifications', 'Target: Content type'),
        related_name='notification_target', on_delete=models.SET_NULL,
    )
    target_object_id = models.CharField(
        verbose_name=pgettext_lazy('wcd_notifications', 'Target: Id'),
        max_length=255, null=True, blank=True,
    )
    target = GenericForeignKey('target_content_type', 'target_object_id')

    flags = ArrayField(
        models.PositiveIntegerField(),
        verbose_name=pgettext_lazy('wcd_notifications', 'Flags'),
        null=False, blank=True, default=list,
    )
    message = models.TextField(
        verbose_name=pgettext_lazy('wcd_notifications', 'Message'),
        null=False, blank=False,
    )

    data = JSONField(
        verbose_name=pgettext_lazy('wcd_notifications', 'Data'),
        blank=True, null=False, default=dict,
    )
    sent_at = models.DateTimeField(default=timezone.now, db_index=True)
    created_at = models.DateTimeField(default=timezone.now, db_index=True)
    ordering_field = models.BigIntegerField(db_index=True, editable=False)

    def __str__(self):
        return self.message

    def prepare(
        self,
        force_insert: bool = False,
        force_update: bool = False,
        using: Optional[str] = None,
        update_fields: Optional[Iterable[str]] = None,
    ):
        result = self.preparator({
            'instance': self,
            'force_insert': force_insert,
            'force_update': force_update,
            'using': using,
            'update_fields': update_fields,
        })
        result.setdefault('force_insert', force_insert)
        result.setdefault('force_update', force_update)
        result.setdefault('using', using)
        result.setdefault('update_fields', update_fields)

        return result

    def save(self, **kwargs) -> None:
        prepared = self.prepare(**kwargs)

        return super().save(
            force_insert=prepared['force_insert'],
            force_update=prepared['force_update'],
            using=prepared['using'],
            update_fields=prepared['update_fields'],
        )


Notification.flags_registry.add(Notification.Readability)


def _set_update_field_context(context: dict, value: str):
    if 'update_field' in context and context['update_field']:
        if not isinstance(context['update_field'], list):
            context['update_field'] = list(context['update_field'])

        context['update_field'].append(value)


@Notification.preparator.add
def prepare_ordering(context: dict):
    _set_update_field_context(context, 'ordering_field')
    instance: Notification = context['instance']
    instance.ordering_field = int(instance.sent_at.timestamp() * 1000)

    return context


@Notification.preparator.add
def set_readability_state(context: dict):
    instance: Notification = context['instance']

    if set(instance.flags) & set(x.value for x in Notification.Readability):
        return

    _set_update_field_context(context, 'flags')
    instance.flags.append(Notification.Readability.UNREAD)

    return context
