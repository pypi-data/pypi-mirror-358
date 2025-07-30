import pytest
from pprint import pprint

from django.contrib.auth.models import Permission
from wcd_notifications.services import notifier
from wcd_notifications.contrib.drf.views import notifications_clear_view
from wcd_notifications.models.notifications import Notification
from wcd_notifications.utils import get_type_pk_pair, to_content_type_key


@pytest.mark.django_db
def test_clear_view(rf, make_user, django_assert_num_queries):
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
        f'/set-flags/?ids={notifications[2].pk}',
        {'flags': Notification.Readability.READ},
    )
    request.user = user
    assert Notification.objects.count() == 3
    response = notifications_clear_view(request)

    assert response.status_code == 200
    assert response.data['cleared'] == 1
    assert Notification.objects.count() == 2
