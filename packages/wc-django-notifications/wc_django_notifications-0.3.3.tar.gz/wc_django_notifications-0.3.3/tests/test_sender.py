import pytest
from pprint import pprint

from wcd_notifications.models import Notification
from wcd_notifications.services import notifier
from wcd_notifications.signals import notifications_sent, notifications_updated

from .utils import mute_signals


@pytest.mark.django_db
def test_simple_send(make_user, django_assert_num_queries):
    user, _ = make_user('1')
    user2, _ = make_user('2')

    with django_assert_num_queries(1):
        with mute_signals(notifications_sent, notifications_updated):
            notifications = notifier.send(
                'Found some {actor} for you {recipient}', [user, user2],
                actor=user,
            )

    assert len(notifications[0].flags) == 1
    assert notifications[0].flags[0] == Notification.Readability.UNREAD

    # Runs with state update:
    with django_assert_num_queries(6):
        notifications = notifier.send(
            'Found some {actor} for you {recipient}', [user, user2],
            actor=user,
        )
