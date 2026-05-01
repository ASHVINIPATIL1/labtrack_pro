# Generated manually for device field updates
import django.db.models
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('labs', '0004_alter_device_category_alter_device_status'),
    ]

    operations = [
        migrations.AddField(
            model_name='device',
            name='ip_address',
            field=models.GenericIPAddressField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='device',
            name='device_configuration',
            field=models.TextField(blank=True, default=''),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='device',
            name='os_name',
            field=models.TextField(blank=True, default=''),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='device',
            name='software_details',
            field=models.TextField(blank=True, default=''),
            preserve_default=False,
        ),
    ]
