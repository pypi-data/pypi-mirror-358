from operator import or_
from django import forms
from django.utils.encoding import force_str
from django.contrib.contenttypes.models import ContentType
from django.utils.translation import pgettext_lazy
from django.db import models

from django_filters import rest_framework as filters
from django_filters import fields
from django_filters import widgets
from django_filters.constants import EMPTY_VALUES

from wcd_notifications.models import Notification, Stats
from wcd_notifications.utils import from_content_type_key


class SplitterWidget(widgets.BaseCSVWidget):
    delimiter = ','

    def __init__(self, *args, **kwargs):
        self.delimiter = kwargs.pop('delimiter', self.delimiter)
        super().__init__(*args, **kwargs)

    def value_from_datadict(self, data, files, name):
        try:
            getter = data.getlist
        except AttributeError:
            getter = data.get

        values = getter(name)

        if not isinstance(values, (list, tuple, set)):
            values = [values]

        normalized = (
            [] if x == '' or x is None else x.split(self.delimiter)
            for x in values
        )

        return [
            [y for y in x if y is not None]
            for x in normalized
            if x is not None and len(x) > 0
        ]

    def render(self, name, value, attrs=None, renderer=None):
        if not self._isiterable(value):
            value = [value]

        if len(value) <= 1:
            # delegate to main widget (Select, etc...) if not multiple values
            value = value[0] if value else ""
            return super().render(name, value, attrs, renderer=renderer)

        # if we have multiple values, we need to force render as a text input
        # (otherwise, the additional values are lost)
        value = [force_str(self.surrogate.format_value(v)) for v in value]
        value = self.delimiter.join(list(value))

        return self.surrogate.render(name, value, attrs, renderer=renderer)


class FlatSplitterWidget(SplitterWidget):
    def value_from_datadict(self, data, files, name):
        lists = super().value_from_datadict(data, files, name)

        return [y for x in lists for y in x]


class SplitterField(fields.BaseCSVField):
    widget = SplitterWidget


class FlatSplitterField(SplitterField):
    widget = FlatSplitterWidget


class GenericKeySplitterField(FlatSplitterField):
    type_pk_delimiter = '~'
    default_error_messages = {
        'key_invalid': pgettext_lazy('wcd_notifications', 'Key is invalid.'),
        'no_content_type': pgettext_lazy('wcd_notifications', 'No such content type exists.'),
    }

    def __init__(self, *args, **kwargs):
        self.type_pk_delimiter = kwargs.pop('type_pk_delimiter', self.type_pk_delimiter)
        super().__init__(*args, **kwargs)

    def clean(self, values):
        values = super().clean(values)
        result = []

        for value in values:
            ct, oid, *_ = value.split(self.type_pk_delimiter) + [None, None]

            if not ct or not oid:
                raise forms.ValidationError(
                    self.error_messages['key_invalid'], code='key_invalid',
                )

            try:
                content_type = from_content_type_key(ct)
            except ContentType.DoesNotExist:
                raise forms.ValidationError(
                    self.error_messages['no_content_type'],
                    code='no_content_type',
                )

            result.append((content_type, oid))

        return result


class ContentTypeSplitterField(FlatSplitterField):
    default_error_messages = {
        'no_content_type': pgettext_lazy('wcd_notifications', 'No such content type exists.'),
    }

    def clean(self, values):
        values = super().clean(values)
        result = []

        for value in values:
            if not value or value.isspace():
                if self.required:
                    raise forms.ValidationError(
                        self.error_messages['required'],
                        code='required',
                    )
                continue

            try:
                content_type = from_content_type_key(value)
            except ContentType.DoesNotExist:
                raise forms.ValidationError(
                    self.error_messages['no_content_type'],
                    code='no_content_type',
                )

            result.append(content_type)

        return result


class LookupMultiplicationFilter(filters.BaseInFilter):
    base_field_class = SplitterField
    operator = or_

    def __init__(self, *args, **kwargs):
        self.operator = kwargs.pop('operator', self.operator)
        super().__init__(*args, **kwargs)

    def filter(self, qs, value):
        if value in EMPTY_VALUES:
            return qs
        if self.distinct:
            qs = qs.distinct()
        lookup = "%s__%s" % (self.field_name, self.lookup_expr)

        q = models.Q()

        for element in value:
            q = self.operator(q, models.Q(**{lookup: element}))

        qs = self.get_method(qs)(q)
        return qs


class InFilter(filters.BaseInFilter):
    base_field_class = FlatSplitterField


class NumbersInFilter(InFilter, filters.NumberFilter):
    pass


class QuerySetMethodFilter(InFilter):
    def __init__(self, *args, **kwargs):
        self.qs_method = kwargs.pop('qs_method')
        super().__init__(*args, **kwargs)

    def get_method(self, qs):
        return getattr(qs, self.qs_method)

    def filter(self, qs, value):
        if value in EMPTY_VALUES:
            return qs
        if self.distinct:
            qs = qs.distinct()

        qs = self.get_method(qs)(value)
        return qs


class GenericKeyMethodFilter(QuerySetMethodFilter):
    base_field_class = GenericKeySplitterField


class ContentTypeInFilter(InFilter):
    base_field_class = ContentTypeSplitterField


class BaseFilterSet(filters.FilterSet):
    ids = NumbersInFilter(field_name='pk', lookup_expr='in')


class NotificationsFilterSet(BaseFilterSet):
    actors = GenericKeyMethodFilter(qs_method='actors')
    actions = GenericKeyMethodFilter(qs_method='actions')
    targets = GenericKeyMethodFilter(qs_method='targets')

    actor_types = ContentTypeInFilter(field_name='actor_content_type', lookup_expr='in')
    action_types = ContentTypeInFilter(field_name='action_content_type', lookup_expr='in')
    target_types = ContentTypeInFilter(field_name='target_content_type', lookup_expr='in')

    parents = NumbersInFilter(field_name='parent_id', lookup_expr='in')
    flags = LookupMultiplicationFilter(field_name='flags', lookup_expr='contains')
    flags_except = LookupMultiplicationFilter(
        field_name='flags', lookup_expr='contains', exclude=True,
    )

    sent_at = filters.IsoDateTimeFromToRangeFilter()

    is_sent = filters.BooleanFilter(method='filter_sent')
    is_root = filters.BooleanFilter(method='filter_roots')

    class Meta:
        model = Notification
        fields = [
            'ids',
            'actors', 'actions', 'targets',
            'actor_types', 'action_types', 'target_types',
            'parents', 'flags', 'flags_except',
            'sent_at',
            'is_sent', 'is_root',
        ]

    def filter_sent(self, qs, value):
        if value is not True:
            return qs

        return qs.sent()

    def filter_roots(self, qs, value):
        if value is not True:
            return qs

        return qs.filter(parent_id__isnull=True)


class StatsFilterSet(filters.FilterSet):
    actor_types = ContentTypeInFilter(field_name='actor_content_type', lookup_expr='in')
    action_types = ContentTypeInFilter(field_name='action_content_type', lookup_expr='in')
    target_types = ContentTypeInFilter(field_name='target_content_type', lookup_expr='in')

    class Meta:
        model = Stats
        fields = ['actor_types', 'action_types', 'target_types']
