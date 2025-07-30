from django.core.management.base import BaseCommand

from wcd_notifications.services import manager
from wcd_notifications.models import Notification
from wcd_notifications.utils import from_content_type_key


class Command(BaseCommand):
    help = 'Collecting stats in case of some failures.'

    def add_arguments(self, parser):
        parser.add_argument('-r', '--recipients', nargs='+', default=[])

    def handle(self, *args, recipients=[], **options):
        qs = Notification.objects.all()

        if len(recipients) != 0:
            qs = qs.recipients(
                (from_content_type_key(ct), oid) for ct, oid, *_ in (
                    y.split('~') + [None, None] for y in recipients
                )
            )

        resolved_recipients = qs.collect_recipients()

        if len(resolved_recipients) > 0:
            manager.collect_stats(resolved_recipients)

        print(f'Collected statistics for {len(resolved_recipients)} recipients.')
