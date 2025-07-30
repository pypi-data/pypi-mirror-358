import pytest
from pprint import pprint

from django.contrib.auth.models import Permission
from wcd_notifications.services import notifier
from wcd_notifications.contrib.drf.views import (
    notifications_list_view, flags_list_view
)
from wcd_notifications.models.notifications import Notification
from wcd_notifications.utils import get_type_pk_pair, to_content_type_key


@pytest.mark.django_db
def test_flags_list_view(rf, django_assert_num_queries):
    request = rf.get('/list/')

    with django_assert_num_queries(0):
        response = flags_list_view(request)

    assert response.status_code == 200
    assert len(response.data) == 2
    assert {x['id'] for x in response.data} == {x for x in Notification.Readability}


@pytest.mark.django_db
def test_notifications_list_view(rf, make_user, django_assert_num_queries):
    user, _ = make_user('1')
    request = rf.get('/list/')
    request.user = user
    response = notifications_list_view(request)

    assert response.status_code == 200
    assert len(response.data) == 0

    user2, _ = make_user('2')
    notifications = notifier.send(
        'Found some {actor} for you {recipient}', [user, user2],
        actor=user,
        flags=[Notification.Readability.UNREAD],
    )

    # FIXME: Make them to be only 2.
    with django_assert_num_queries(3):
        response = notifications_list_view(request)

    assert response.status_code == 200
    assert len(response.data) == 1
    assert response.data[0]['message'] == 'Found some 1 for you 1'

    # FIXME: Make them to be only 2.
    request.user = user2
    with django_assert_num_queries(3):
        response = notifications_list_view(request)

    assert response.status_code == 200
    assert len(response.data) == 1
    assert response.data[0]['message'] == 'Found some 1 for you 2'


@pytest.mark.django_db
def test_list_filtering_view(rf, make_user, django_assert_num_queries):
    user, _ = make_user('1')
    user2, _ = make_user('2')
    user3, _ = make_user('3')
    ct, oid = get_type_pk_pair(user2)
    permission = Permission.objects.create(
        content_type=ct, name='some', codename='some'
    )
    pct, poid = get_type_pk_pair(permission)

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

    request = rf.get(
        f'/list/'
        f'?ids={notifications[0].pk}&ids={notifications[2].pk}'
    )
    request.user = user
    response = notifications_list_view(request)

    assert response.status_code == 200
    assert len(response.data) == 2

    request = rf.get(f'/list/?ids={notifications[0].pk}')
    request.user = user
    with django_assert_num_queries(3):
        response = notifications_list_view(request)

    assert response.status_code == 200
    assert len(response.data) == 1
    assert response.data[0]['message'] == 'Found some 1 for you 1'

    request = rf.get(
        f'/list/'
        f'?ids={notifications[0].pk}&ids={notifications[2].pk}'
        f'&actors={to_content_type_key(ct)}~{oid}'
    )
    request.user = user
    with django_assert_num_queries(3):
        response = notifications_list_view(request)

    assert response.status_code == 200
    assert len(response.data) == 1
    assert response.data[0]['message'] == 'Found some 2 for you 1'

    notifications += notifier.send(
        'Found some {actor} for you {recipient}', [user],
        actor=permission,
        flags=[Notification.Readability.READ],
    )
    request = rf.get(
        f'/list/'
        f'?actor_types={to_content_type_key(pct)}'
    )
    request.user = user
    with django_assert_num_queries(4):
        response = notifications_list_view(request)

    assert response.status_code == 200
    assert len(response.data) == 1
    assert response.data[0]['message'] == 'Found some auth | user | some for you 1'

    request = rf.get(
        f'/list/'
        f'?sent_at_after={notifications[-2].sent_at.isoformat()}'
    )
    request.user = user
    # FIXME: Must be 2 here:
    with django_assert_num_queries(5):
        response = notifications_list_view(request)

    assert response.status_code == 200
    assert len(response.data) == 2
    assert response.data[0]['message'] == 'Found some auth | user | some for you 1'
    assert response.data[1]['message'] == 'Found some 2 for you 1'

    request = rf.get(
        f'/list/'
        f'?sent_at_before={notifications[-2].sent_at.isoformat()}'
    )
    request.user = user
    # FIXME: Must be 2 here:
    with django_assert_num_queries(3):
        response = notifications_list_view(request)

    assert response.status_code == 200
    assert len(response.data) == 2
    assert response.data[0]['message'] == 'Found some 2 for you 1'
    assert response.data[1]['message'] == 'Found some 1 for you 1'

    request = rf.get(
        f'/list/'
        f'?flags={Notification.Readability.UNREAD}'
    )
    request.user = user
    # FIXME: Must be 2 here:
    with django_assert_num_queries(3):
        response = notifications_list_view(request)

    assert response.status_code == 200
    assert len(response.data) == 2

    # OR operator here:
    request = rf.get(
        f'/list/'
        f'?flags={Notification.Readability.UNREAD}&flags={Notification.Readability.READ}'
    )
    request.user = user
    # FIXME: Must be 2 here:
    with django_assert_num_queries(5):
        response = notifications_list_view(request)

    assert response.status_code == 200
    assert len(response.data) == 3

    # Since there is "and" - it find nothing:
    request = rf.get(
        f'/list/'
        f'?flags={Notification.Readability.UNREAD},{Notification.Readability.READ}'
    )
    request.user = user
    # FIXME: Must be 2 here:
    with django_assert_num_queries(1):
        response = notifications_list_view(request)

    assert response.status_code == 200
    assert len(response.data) == 0
