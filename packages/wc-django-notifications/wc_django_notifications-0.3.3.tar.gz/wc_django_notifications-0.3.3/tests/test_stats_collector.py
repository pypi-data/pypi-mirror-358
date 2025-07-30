import pytest
from pprint import pprint

from wcd_notifications.services import notifier, manager
from wcd_notifications.models.notifications import Notification
from wcd_notifications.contrib.drf.views import stats_list_view
from wcd_notifications.signals import notifications_sent, notifications_updated

from .utils import mute_signals


@pytest.mark.django_db
def test_stats_collect_mechanics(rf, make_user, django_assert_num_queries):
    user, _ = make_user('1')
    user2, _ = make_user('2')

    with mute_signals(notifications_sent, notifications_updated):
        notifications = notifier.send(
            'Found some {actor} for you {recipient}', [user, user2],
            actor=user,
            flags=[Notification.Readability.UNREAD],
        )
        notifications += notifier.send(
            'Found some {actor} for you {recipient}', [user],
            actor=user2,
            flags=[Notification.Readability.UNREAD],
        )
        notifications += notifier.send(
            'Found some {actor} for you {recipient}', [user],
            actor=user,
            flags=[Notification.Readability.READ],
        )

    with django_assert_num_queries(5):
        stats = manager.collect_stats([user])

    total_stats = next(x for x in stats if x.flag == manager.TOTAL_FLAG)
    unread_stats = next(x for x in stats if x.flag == Notification.Readability.UNREAD)
    read_stats = next(x for x in stats if x.flag == Notification.Readability.READ)

    assert len(stats) == 3
    assert total_stats.amount == 3
    assert unread_stats.amount == 2
    assert read_stats.amount == 1

    ids = {x.pk for x in stats}

    with django_assert_num_queries(5):
        assert {x.pk for x in manager.collect_stats([user])} == ids

    # FIXME: Should rework the stats collector to lower the number of queries
    with django_assert_num_queries(5):
        stats2 = manager.collect_stats([user2])

    total_stats = next(x for x in stats2 if x.flag == manager.TOTAL_FLAG)
    unread_stats = next(x for x in stats2 if x.flag == Notification.Readability.UNREAD)

    assert len(stats2) == 2
    assert total_stats.amount == 1
    assert unread_stats.amount == 1


@pytest.mark.django_db
def test_stats_view(rf, make_user, django_assert_num_queries):
    user, _ = make_user('1')
    user2, _ = make_user('2')

    with mute_signals(notifications_sent, notifications_updated):
        notifications = notifier.send(
            'Found some {actor} for you {recipient}', [user, user2],
            actor=user,
            flags=[Notification.Readability.UNREAD],
        )
        notifications += notifier.send(
            'Found some {actor} for you {recipient}', [user],
            actor=user2,
            flags=[Notification.Readability.UNREAD],
        )
    notifications += notifier.send(
        'Found some {actor} for you {recipient}', [user],
        actor=user,
        flags=[Notification.Readability.READ],
    )

    request = rf.get('/stats/')
    request.user = user
    response = stats_list_view(request)

    assert response.status_code == 200
    assert len(response.data) == 1

    stat = response.data[0]

    assert stat['recipient']['id'] == user.pk
    assert stat['total'] == 3
    assert stat['flags'][Notification.Readability.UNREAD] == 2
    assert stat['flags'][Notification.Readability.READ] == 1
