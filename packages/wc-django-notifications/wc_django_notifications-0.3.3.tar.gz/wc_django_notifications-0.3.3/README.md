# Django notifications

Modular notifications system for your django applications.

## Installation

```sh
pip install wc-django-notifications
```

In `settings.py`:

```python
INSTALLED_APPS += [
  # ...
  'wcd_notifications',
]

WCD_NOTIFICATIONS = {
  # Resolving function to get recipients from request.
  # Using mostly by API.
  'RECIPIENTS_RESOLVER': 'wcd_notifications.utils.default_resolve_recipients',
  # Pipeline functions for additional notifications instances preparation.
  'PREPARATION_PIPELINE': [],
  # Pipeline functions that handle notification flag changes.
  'CHANGE_FLAG_PIPELINE': [
    # Resolves readability flags intersection.
    'wcd_notifications.services.manager.set_readability_flags_operation',
  ],
}
```

## Usage

### Sending notifications

```python
from wcd_notifications.services import notifier


notifications = notifier.send(
  # Simple formattable string.
  # `.format` method will be applied during `send` event.
  # For example:
  '{actor} created new {action} after leaving {target}.',
  # Recipient objects list.
  [user1, user2],
  # Optional. Object that performed activity.
  actor=None,
  # Optional. Action object, that was performed.
  action=None,
  # Optional. Target object to which the activity was performed.
  target=None,
  # Parent notification. If exists.
  parent=None,
  # Initial flags that a message will have.
  flags=[],
  # Some extra data that will be stored in json field.
  extra={},
  # Recipients can receive this message after some time.
  send_at=None,
  # Can send with different current time.
  now=None,
  batch_size=None,
)
```

Notifications send method has several breakpoints on which you may add additional handlers for a common situations:

1. Each notification separately will run preparation pipeline from `Notification.preparator`. It's an instances of `px_pipline.Filter` so you may add or remove them.
2. Then preparation pipeline from `settings.PREPARATION_PIPELINE` will be run on all new notification instances.
3. Notifications will be created.
4. For each notification `wcd_notifications.signals.notification_sent` will be sent.
4. For all new notifications `wcd_notifications.signals.notifications_sent` will be sent.
5. There is already one `wcd_notifications.signals.notifications_sent` signal reciever. It will recollect stats for all the recipients that new notifications has.

### Notification state management

You may change flags in three different ways:

- `add` - List of flags to add.
- `remove` - List of flags to remove.
- `specify` - List of flags to set hard. `add` and `remove` parameters i this case will be ignored.

```python
from wcd_notifications.services import manager


# For example we need to mark some notifications as `read`:
manager.change_flags(
  Notification.objects.all(),
  add=[Notification.Readability.READ],
  # Empty specify list will be ignored.
  specify=[],
)
```

Only read/unread flags are not enough. And you may use any numbers you wish as flags. It would be better to use `django.db.models.IntegerChoices` or at least `enum.Enum` to define different state groups.

And it will be better if library could know about your flags.

For this case there is a simple flags registry:

```python
from enum import Enum

from wcd_notifications.models import Notification


class OtherOptions(int, Enum):
  ONE = 1
  TWO = 2


# By running this command you register your flags:
Notification.flags_registry.add(OtherOptions)
```

Flags change method also has it's own breakpoints to extend:

1. After all flag changes applied, but not saved pipeline from `settings.CHANGE_FLAG_PIPELINE` runs.
2. All notification flags changes are saved to database.
3. Signal `wcd_notifications.signals.notifications_flags_changed` sent.
3. Signal `wcd_notifications.signals.notifications_updated` sent.

### Querying

Notifications queryset has additional methods, for easier querying:

```python
from wcd_notifications.models import Notification


qs = (
  Notification.objects
  # To find only read notifications.
  .read()
  # To find only new notifications.
  .unread()
  # To filter by recipients:
  .recipients([])
  # Actors:
  .actors([])
  # Actions:
  .actions([])
  # Targets:
  .targets([])
  # To display only already sent messages.
  .sent(now=None)
)
```

### Stats

Reading information about notifications state is far more frequent action, that notifications change/sending. So library "caches" state data into database and updates it after any change occured.

There is only one simple SELECT operation to get state for any recipients:

```python
from wcd_notifications.models import Stats


# For one recipient there is at most one stats object exists.
user_stats = Stats.objects.recipients([user]).first()
```

Collecting stats are automatically happens in management methods. But there could be cases when notifications are updated by hand. In that case you should collect stats manually:

```python
from wcd_notifications.services import manager


# You may pass a recipients list here or manual `None` if stats for all
# recipients must be updated.
manager.collect_stats([user1])
```

## Contrib

### DRF

There are ready for use frontend for django rest framework.

```python
INSTALLED_APPS += [
  # ...
  'wcd_notifications.contrib.drf',

  # Django filters required for api to work.
  'django_filters',
  'rest_framework',
]

In `urls.py`:

```python
from wcd_notifications.contrib.drf.views import make_urlpatterns

urlpatters = [
  ...
  path('api/v1/notifications/', include(make_urlpatterns(
    # Here you can replace any view by your own customized one.
  ))),
]
```

It will add 5 views there:

#### `GET[/api/v1/notifications/flags/list/]`

Returns list of all available flags.

#### `GET[/api/v1/notifications/notifications/list/]`

Paginatable list of notifications.

To be able to display related objects in more detailed manner you may also register serializers that will be used for each object of a particular model:

```python
from wcd_notifications.contrib.drf.serializers import FIELD_SERIALIZERS

from .models import SomeModel
from .serializers import SomeModelSerializer


# So for any object of `SomeModel` `SomeModelSerializer` will be used to
# display `props` in notifications list view.
FIELD_SERIALIZERS.add(SomeModel, SomeModelSerializer)
```

Also notifications messages can have shortcodes from `wc-shortcodes` and will be transformed during render. You only need to register your custom shortodes:

```python
from wcd_notifications.contrib.drf.serializers import SHORTCODES_REGISTRY


@SHORTCODES_REGISTRY.register()
def shortcode(entity, context={}):
  return entity.content
```

Filters that can be applied:

- **ids**: List of identifiers to filter over:

  `&ids=1,2,3&ids=4,6` - There can be mutiple same named fields. Comma ',' could be also a separator for multiple values. Or operator used for all identifiers.

- **actors**: List of actors to filter on:

  `&actors=auth.user~1,auth.user~2&actors=auth.user~4` - There can be mutiple same named fields. Comma ',' could be also a separator for multiple values. Or operator used for all identifiers.

  One value to filter on is: `{object_type}~{object_id}`.

- **actions**: Same as **actors**.
- **targets**: Same as **actors**.
- **actor_types**: List of types for filter on:

  `&actor_types=auth.user,muapp.mymodel&actor_types=otherapp.othermodel` - There can be mutiple same named fields. Comma ',' could be also a separator for multiple values. Or operator used for all identifiers.

- **action_types**: Same as **actor_types**.
- **target_types**: Same as **actor_types**.
- **sent_at_before**: Filter by the time >= notification was sent. ISO datetime.
- **sent_at_after**: Filter by the time <= notification was sent. ISO datetime.
- **is_sent**: Get only already sent notifications.
- **is_root**: Since notifications are hierarchical you may only need a root notifications.
- **parents**: List of parent identifiers to filter over:

  `&parents=1,2,3&parents=4,6` - There can be mutiple same named fields. Comma ',' could be also a separator for multiple values. Or operator used for all identifiers.
- **flags**: Filtering over flags is not that simple OR statement.

  `&flags=1,2,3&flags=4,6` - Each comma ',' separated list considered as AND comparison. Or operator used between multiple `flags` fields.

  So this example will lead to `(1 or 2 or 3) and (4 or 6)` comparison statement.

#### `POST[/api/v1/notifications/notifications/set-flags/]`

To add specific flags to notifications(like `read` for example) you can use this method.

Notifications can be filtered the same way as in `/notifications/list/` view.

Under the hood it uses `manager.change_flags` method, so data it requires works the same:

```json
{
  "add": [1,2,4],
  "remove": [6],
  "specify": []
}
```

#### `POST[/api/v1/notifications/notifications/clear/]`

This view deletes notifications by your will. What notifications should be deleted can be filtered the same way as in `/notifications/list/` view.

#### `GET[/api/v1/notifications/notifications/stats/]`

Here user can get a notifications statistics. There will be a list for each recipient that current authorization resolves in.

Each recipient stats contains total count of notifications and notification counts for every flag exists in their notifications.

So this way you will find all read/unread messages for example.

Filters that can be applied:

- **actor_types**: List of types for filter on:

  `&actor_types=auth.user,muapp.mymodel&actor_types=otherapp.othermodel` - There can be mutiple same named fields. Comma ',' could be also a separator for multiple values. Or operator used for all identifiers.

- **action_types**: Same as **actor_types**.
- **target_types**: Same as **actor_types**.

By applying filters you receive statistics data only for affected notifications.
