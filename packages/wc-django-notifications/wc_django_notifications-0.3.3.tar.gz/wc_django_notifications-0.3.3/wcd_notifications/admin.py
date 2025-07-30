from django.contrib import admin
from django.conf import settings

from .models import Notification, Stats
from .services import manager


formfield_overrides = {}


if 'prettyjson' in settings.INSTALLED_APPS:
    from prettyjson import PrettyJSONWidget
    from .compat import JSONField

    formfield_overrides[JSONField] = {'widget': PrettyJSONWidget}


@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    list_display = 'id', 'message', 'recipient', 'created_at',
    list_filter = (
        'recipient_content_type', 'actor_content_type',
        'action_content_type', 'target_content_type',
    )
    raw_id_fields = 'parent',
    search_fields = (
        'parent__id',
        'recipient_object_id', 'actor_object_id',
        'action_object_id', 'target_object_id',
        'flags', 'message', 'data',
    )
    formfield_overrides = formfield_overrides

    def save_model(self, request, obj, form, change) -> None:
        result = super().save_model(request, obj, form, change)

        if obj.recipient:
            manager.collect_stats([obj.recipient])

        return result


@admin.register(Stats)
class StatsAdmin(admin.ModelAdmin):
    list_display = (
        'id', 'recipient', 'flag', 'amount',
        'recipient_content_type', 'actor_content_type',
        'action_content_type', 'target_content_type',
    )
    list_filter = (
        'recipient_content_type', 'actor_content_type',
        'action_content_type', 'target_content_type',
    )
    list_select_related = list_filter
    search_fields = (
        'recipient_content_type', 'recipient_object_id',
        'flag', 'amount',
    )
