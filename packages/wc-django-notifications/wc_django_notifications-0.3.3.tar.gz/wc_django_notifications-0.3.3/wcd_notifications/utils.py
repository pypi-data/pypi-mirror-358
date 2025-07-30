from itertools import groupby
from operator import attrgetter
from operator import or_
from django.db import models
from django.contrib.contenttypes.models import ContentType
from django.utils.translation import pgettext_lazy
from functools import lru_cache
from collections import OrderedDict
from typing import Callable, List, Optional, Sequence, Tuple, Type, TypeVar, Union
from django.utils.module_loading import import_string

from .conf import settings


NATURAL_KEY_DELIMITER = '.'
M = TypeVar('M', bound=models.Model)
TypePkPair = Tuple[ContentType, Union[str, int]]
ModelDef = Union[models.Model, TypePkPair]


@lru_cache
def cached_import_string(path: str):
    return import_string(path)


def group_and_sort(items, key=lambda x: x, **kwargs):
    return groupby(sorted(items, key=key, **kwargs), key=key)


def get_type_pk_pair(instance: Optional[models.Model] = None):
    if instance is None:
        return None, None

    return ContentType.objects.get_for_model(instance.__class__), instance.pk


def content_type_from_id(id):
    return ContentType.objects.get_for_id(id)if id is not None else None


def to_content_type_key(ct: ContentType):
    return NATURAL_KEY_DELIMITER.join(ct.natural_key())


def from_content_type_key(key: str) -> ContentType:
    splitted = key.split(NATURAL_KEY_DELIMITER)

    if len(splitted) != 2:
        raise ContentType.DoesNotExist(pgettext_lazy(
            'wcd_notifications', 'No content type found for "{}" key.'
        ).format(key))

    return ContentType.objects.get_by_natural_key(*splitted)


def to_intarray(ints: Sequence[int]) -> str:
    return '{' + ','.join(map(str, ints)) + '}'


class Registry(OrderedDict):
    def add(self, key, value):
        assert key not in self, f'{key} already registered.'

        self[key] = value

    register = add


def resolve_generic_field_data(
    obj: models.Model, field_name: str,
) -> Tuple[Optional[ContentType], Optional[str], Optional[models.Model]]:
    if getattr(obj, f'{field_name}_content_type_id') is None:
        return None, None, None

    return (
        getattr(obj, f'{field_name}_content_type'),
        getattr(obj, f'{field_name}_object_id'),
        getattr(obj, field_name),
    )


def make_generic_Q(
    field_name: str,
    values: Sequence[ModelDef],
    operator: Callable = or_
) -> models.Q:
    q = models.Q()
    ctf = f'{field_name}_content_type'
    oidf = f'{field_name}_object_id'

    for value in values:
        ct, oid = get_type_pk_pair(value) if isinstance(value, models.Model) else value
        q = operator(q, models.Q(**{ctf: ct, oidf: oid}))

    return q


def default_resolve_recipients(request, **kw) -> List[models.Model]:
    user = getattr(request, 'user')

    return [user] if user is not None and user.is_authenticated else []


def resolve_recipients(request, **kw) -> List[models.Model]:
    return cached_import_string(settings.RECIPIENTS_RESOLVER)(request, **kw)


def model_bulk_update_or_create(
    model: Type[M], items: Sequence[Tuple[dict, dict]],
    internal_id_name: str = '_internal_lookup_id',
) -> List[M]:
    if len(items) == 0:
        return []

    id_map = {i + 1: value for i, value in enumerate(items)}
    q = models.Q()
    whens = []
    getid = attrgetter(internal_id_name)

    for id, (filters, _) in id_map.items():
        condition = models.Q(**filters)
        q |= condition
        whens.append(models.When(condition, then=models.Value(id)))

    existing = list(
        model.objects
        .filter(q)
        .annotate(**{internal_id_name: models.Case(
            *whens, default=None, output_field=models.IntegerField(),
        )})
    )
    diff = list(id_map.keys() - {getid(x) for x in existing})

    if len(existing) > 0:
        update_fields = set()

        for instance in existing:
            id = getid(instance)

            for field, value in id_map[id][1].items():
                setattr(instance, field, value)
                update_fields.add(field)

        model.objects.bulk_update(existing, fields=update_fields)

    if len(diff) == 0:
        return existing

    blanks = (
        model(**{**id_map[id][0], **id_map[id][1]})
        for id in diff
    )
    created = model.objects.bulk_create(blanks)

    for i, x in enumerate(created):
        setattr(x, internal_id_name, diff[i])

    return sorted(existing + created, key=getid)
