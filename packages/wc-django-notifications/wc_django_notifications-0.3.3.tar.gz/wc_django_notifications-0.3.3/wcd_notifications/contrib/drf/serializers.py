from django.utils.translation import pgettext_lazy

from rest_framework import serializers
from rest_framework import exceptions

from wc_shortcodes.registry import CodesRegistry

from wcd_notifications.models import Notification, Stats
from wcd_notifications.utils import (
    Registry, resolve_generic_field_data, to_content_type_key,
)
from wc_shortcodes.transformer import transform
from wcd_notifications.services import manager


__all__ = (
    'FIELD_SERIALIZERS', 'SHORTCODES_REGISTRY',
    'FlagReadSerializer',
    'NotificationReadSerializer', 'NotificationChangeFlagSerializer',
    'NotificationClearSerializer',
    'StatsReadSerializer',
)


FIELD_SERIALIZERS = Registry()
SHORTCODES_REGISTRY = CodesRegistry()


class FlagReadSerializer(serializers.Serializer):
    id = serializers.IntegerField(source='value')
    label = serializers.CharField(source='name')
    display = serializers.SerializerMethodField()

    def get_display(self, obj):
        return getattr(obj, 'label', obj.name)


class DisplayRelatedFieldMixin:
    field_serializers = FIELD_SERIALIZERS
    shortcodes = SHORTCODES_REGISTRY

    def _display_related_field(self, notification: Notification, field_name: str):
        content_type, id, obj = resolve_generic_field_data(notification, field_name)

        if content_type is None or obj is None:
            return None

        result = {
            'id': id,
            'type': to_content_type_key(content_type),
            'display': str(obj),
        }
        model = content_type.model_class()

        if model in self.field_serializers:
            result['props'] = self.field_serializers[model](instance=obj).data

        return result


class NotificationReadSerializer(DisplayRelatedFieldMixin, serializers.ModelSerializer):
    flags_registry = property(lambda self: Notification.flags_registry)

    class Meta:
        model = Notification
        fields = (
            'id',
            'recipient', 'actor', 'action', 'target',
            'flags', 'message', 'data',
            'sent_at', 'created_at',
        )

    recipient = serializers.SerializerMethodField()
    actor = serializers.SerializerMethodField()
    action = serializers.SerializerMethodField()
    target = serializers.SerializerMethodField()

    message = serializers.SerializerMethodField()

    flags = serializers.SerializerMethodField()

    def get_recipient(self, obj):
        return self._display_related_field(obj, 'recipient')

    def get_actor(self, obj):
        return self._display_related_field(obj, 'actor')

    def get_action(self, obj):
        return self._display_related_field(obj, 'action')

    def get_target(self, obj):
        return self._display_related_field(obj, 'target')

    def get_flags(self, obj):
        registry = self.flags_registry

        return [
            (
                FlagReadSerializer(registry[flag]).data
                if flag in registry else
                {'id': flag}
            )
            for flag in obj.flags
        ]

    def get_message(self, obj):
        view = self.context.get('view')

        return transform(self.shortcodes, obj.message, context={
            'instance': obj,
            'view': view,
            'request': getattr(view, 'request', None),
        })


class NotificationChangeFlagSerializer(serializers.Serializer):
    default_error_messages = {
        'all_empty': pgettext_lazy(
            'wcd_notifications',
            'You must pass at least one flag into either `add` or `remove` '
            'or `specify` field.'
        ),
    }

    add = serializers.ListField(
        child=serializers.IntegerField(), allow_empty=True, min_length=0,
        required=False,
    )
    remove = serializers.ListField(
        child=serializers.IntegerField(), allow_empty=True, min_length=0,
        required=False,
    )
    specify = serializers.ListField(
        child=serializers.IntegerField(), allow_empty=True, min_length=0,
        required=False,
    )

    def validate(self, data):
        add = data.get('add') or []
        remove = data.get('remove') or []
        specify = data.get('specify') or []

        if len(add) == 0 and len(remove) == 0 and len(specify) == 0:
            raise exceptions.ValidationError(
                self.error_messages['all_empty'], 'all_empty'
            )

        return data

    def commit(self, queryset):
        notifications = manager.change_flags(
            queryset,
            add=self.validated_data.get('add') or [],
            remove=self.validated_data.get('remove') or [],
            specify=self.validated_data.get('specify') or [],
        )

        self._data = {'changed': len(notifications)}


class NotificationClearSerializer(serializers.Serializer):
    def commit(self, queryset):
        cleared = manager.clear(queryset)

        self._data = {'cleared': cleared}


class StatsReadSerializer(DisplayRelatedFieldMixin, serializers.Serializer):
    recipient = serializers.SerializerMethodField()
    flags = serializers.JSONField()
    total = serializers.IntegerField()

    def get_recipient(self, obj):
        return self._display_related_field(obj, 'recipient')
