from django.db import migrations, models


def fill_registration_ids(apps, schema_editor):
    Rsvp = apps.get_model('program', 'Rsvp')
    for index, rsvp in enumerate(Rsvp.objects.order_by('created_at', 'id'), start=1):
        rsvp.registration_id = f'TKMK{index:03d}'
        rsvp.save(update_fields=['registration_id'])


def clear_registration_ids(apps, schema_editor):
    Rsvp = apps.get_model('program', 'Rsvp')
    Rsvp.objects.update(registration_id=None)


class Migration(migrations.Migration):

    dependencies = [
        ('program', '0002_alter_rsvp_phone_number'),
    ]

    operations = [
        migrations.AddField(
            model_name='rsvp',
            name='registration_id',
            field=models.CharField(blank=True, max_length=20, null=True),
        ),
        migrations.RunPython(fill_registration_ids, clear_registration_ids),
        migrations.AlterField(
            model_name='rsvp',
            name='registration_id',
            field=models.CharField(editable=False, max_length=20, unique=True),
        ),
    ]
