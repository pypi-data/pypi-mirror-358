from django.core.management.base import BaseCommand

from wcd_notifications.services import manager
from wcd_notifications.models import Notification, Stats
from wcd_notifications.utils import from_content_type_key, make_generic_Q


class Command(BaseCommand):
    help = 'Clearing notifications and stats for recipients that are not exists.'

    def handle(self, *args, recipients=[], **options):
        qs = Notification.objects.all()
        recipients = set(qs.collect_recipients()) - {None}
        r_n, _ = qs.exclude(make_generic_Q('recipient', recipients)).delete()
        r_s, _ = Stats.objects.exclude(make_generic_Q('recipient', recipients)).delete()

        print(f'Cleared {r_n} notifications and {r_s} stats objects.')
