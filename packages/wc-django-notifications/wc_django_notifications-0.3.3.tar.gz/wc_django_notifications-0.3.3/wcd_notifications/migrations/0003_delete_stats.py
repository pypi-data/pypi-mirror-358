from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('wcd_notifications', '0002_auto_20230616_1153'),
    ]

    operations = [
        migrations.DeleteModel(
            name='Stats',
        ),
    ]
