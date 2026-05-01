from django.db import migrations, models


def convert_active_to_working(apps, schema_editor):
    Device = apps.get_model('labs', 'Device')
    Device.objects.filter(status='active').update(status='working')


def reverse_convert_working_to_active(apps, schema_editor):
    Device = apps.get_model('labs', 'Device')
    Device.objects.filter(status='working').update(status='active')


class Migration(migrations.Migration):

    dependencies = [
        ('labs', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='device',
            name='os_name',
            field=models.CharField(blank=True, default='None', max_length=100),
        ),
        migrations.AddField(
            model_name='device',
            name='software_details',
            field=models.CharField(blank=True, default='None', max_length=200),
        ),
        migrations.RunPython(convert_active_to_working, reverse_code=reverse_convert_working_to_active),
    ]
