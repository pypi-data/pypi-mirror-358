import pytest
from pprint import pprint

from django.contrib.auth.models import Permission
from wcd_notifications.services import notifier
from wcd_notifications.contrib.drf.views import notifications_change_flags_view
from wcd_notifications.models.notifications import Notification
from wcd_notifications.utils import get_type_pk_pair, to_content_type_key


@pytest.mark.django_db
def test_flags_change_view(rf, make_user, django_assert_num_queries):
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

    request = rf.post(
        f'/change-flags/?ids={notifications[2].pk}',
    )
    request.user = user
    response = notifications_change_flags_view(request)

    assert response.status_code == 400

    request = rf.post(
        f'/change-flags/?ids={notifications[2].pk}',
        {'add': [Notification.Readability.READ]},
    )
    request.user = user
    response = notifications_change_flags_view(request)
    mapped = {x: y for x, y in Notification.objects.values_list('pk', 'flags')}

    assert response.status_code == 200
    assert response.data['changed'] == 1
    assert set(mapped[notifications[2].pk]) == {Notification.Readability.READ}

    request = rf.post(
        f'/change-flags/?ids={notifications[2].pk}',
        {'remove': [Notification.Readability.READ]},
    )
    request.user = user
    response = notifications_change_flags_view(request)
    mapped = {x: y for x, y in Notification.objects.values_list('pk', 'flags')}

    assert response.status_code == 200
    assert response.data['changed'] == 1
    assert set(mapped[notifications[2].pk]) == {Notification.Readability.UNREAD}

    request = rf.post(
        f'/change-flags/?ids={notifications[2].pk}',
        {'add': [Notification.Readability.READ]},
    )
    request.user = user
    response = notifications_change_flags_view(request)
    mapped = {x: y for x, y in Notification.objects.values_list('pk', 'flags')}

    assert response.status_code == 200
    assert response.data['changed'] == 1
    assert set(mapped[notifications[2].pk]) == {Notification.Readability.READ}

    request = rf.post('/change-flags/', {'specify': Notification.Readability.READ})
    request.user = user
    response = notifications_change_flags_view(request)
    mapped = {x: y for x, y in Notification.objects.values_list('pk', 'flags')}

    assert response.status_code == 200
    assert response.data['changed'] == 1
    assert set(mapped[notifications[2].pk]) == {Notification.Readability.READ}
    assert set(mapped[notifications[0].pk]) == {Notification.Readability.READ}
    assert set(mapped[notifications[1].pk]) == {Notification.Readability.UNREAD}

    request = rf.post('/change-flags/', {'specify': Notification.Readability.UNREAD})
    request.user = user
    response = notifications_change_flags_view(request)
    mapped = {x: y for x, y in Notification.objects.values_list('pk', 'flags')}

    assert response.status_code == 200
    assert response.data['changed'] == 2


@pytest.mark.django_db
def test_flags_add_logic(rf, make_user, django_assert_num_queries):
    user, _ = make_user('1')
    user2, _ = make_user('2')
    user3, _ = make_user('3')
    ct, oid = get_type_pk_pair(user2)
    permission = Permission.objects.create(
        content_type=ct, name='some', codename='some'
    )
    pct, poid = get_type_pk_pair(permission)

    ONE = 1001
    TWO = 1002
    THREE = 1003

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

    request = rf.post(
        f'/change-flags/?ids={notifications[2].pk}',
        {'add': [ONE]},
    )
    request.user = user
    response = notifications_change_flags_view(request)
    mapped = {x: y for x, y in Notification.objects.values_list('pk', 'flags')}

    assert response.status_code == 200
    assert response.data['changed'] == 1
    assert set(mapped[notifications[2].pk]) == {Notification.Readability.UNREAD, ONE}

    request = rf.post(
        f'/change-flags/?ids={notifications[2].pk}',
        {'add': [Notification.Readability.READ]},
    )
    request.user = user
    response = notifications_change_flags_view(request)
    mapped = {x: y for x, y in Notification.objects.values_list('pk', 'flags')}

    assert response.status_code == 200
    assert response.data['changed'] == 1
    assert set(mapped[notifications[2].pk]) == {Notification.Readability.READ, ONE}

    request = rf.post(
        f'/change-flags/?ids={notifications[2].pk}',
        {'add': [TWO, Notification.Readability.UNREAD]},
    )
    request.user = user
    response = notifications_change_flags_view(request)
    mapped = {x: y for x, y in Notification.objects.values_list('pk', 'flags')}

    assert response.status_code == 200
    assert response.data['changed'] == 1
    assert set(mapped[notifications[2].pk]) == {Notification.Readability.UNREAD, ONE, TWO}

    request = rf.post(
        f'/change-flags/?ids={notifications[2].pk}',
        {'add': [Notification.Readability.READ], 'remove': [TWO]},
    )
    request.user = user
    response = notifications_change_flags_view(request)
    mapped = {x: y for x, y in Notification.objects.values_list('pk', 'flags')}

    assert response.status_code == 200
    assert response.data['changed'] == 1
    assert set(mapped[notifications[2].pk]) == {Notification.Readability.READ, ONE}

    request = rf.post(
        f'/change-flags/?ids={notifications[2].pk}',
        {'add': [THREE]},
    )
    request.user = user
    response = notifications_change_flags_view(request)
    mapped = {x: y for x, y in Notification.objects.values_list('pk', 'flags')}

    assert response.status_code == 200
    assert response.data['changed'] == 1
    assert set(mapped[notifications[2].pk]) == {Notification.Readability.READ, ONE, THREE}

    request = rf.post(
        f'/change-flags/?ids={notifications[2].pk}',
        {'remove': [THREE]},
    )
    request.user = user
    response = notifications_change_flags_view(request)
    mapped = {x: y for x, y in Notification.objects.values_list('pk', 'flags')}

    assert response.status_code == 200
    assert response.data['changed'] == 1
    assert set(mapped[notifications[2].pk]) == {Notification.Readability.READ, ONE}

    request = rf.post(
        f'/change-flags/?ids={notifications[2].pk}',
        {'add': [TWO], 'remove': [Notification.Readability.READ]},
    )
    request.user = user
    response = notifications_change_flags_view(request)
    mapped = {x: y for x, y in Notification.objects.values_list('pk', 'flags')}

    assert response.status_code == 200
    assert response.data['changed'] == 1
    assert set(mapped[notifications[2].pk]) == {Notification.Readability.UNREAD, ONE, TWO}

    request = rf.post(
        f'/change-flags/?ids={notifications[2].pk}',
        {'remove': [Notification.Readability.UNREAD]},
    )
    request.user = user
    response = notifications_change_flags_view(request)
    mapped = {x: y for x, y in Notification.objects.values_list('pk', 'flags')}

    assert response.status_code == 200
    assert response.data['changed'] == 1
    # TODO: Weird, but there should be at least the default state and that is UNREAD
    assert set(mapped[notifications[2].pk]) == {Notification.Readability.UNREAD, ONE, TWO}
