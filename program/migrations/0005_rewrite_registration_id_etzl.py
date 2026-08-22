from django.db import migrations


def rewrite_registration_ids(apps, schema_editor):
    Rsvp = apps.get_model('program', 'Rsvp')
    # Temporary unique values first to avoid unique conflicts while renaming.
    for index, rsvp in enumerate(Rsvp.objects.order_by('created_at', 'id'), start=1):
        rsvp.registration_id = f'TMP{index:05d}'
        rsvp.save(update_fields=['registration_id'])
    for index, rsvp in enumerate(Rsvp.objects.order_by('created_at', 'id'), start=1):
        rsvp.registration_id = f'ETZL{index:02d}'
        rsvp.save(update_fields=['registration_id'])


def noop_reverse(apps, schema_editor):
    pass


class Migration(migrations.Migration):

    dependencies = [
        ('program', '0004_rsvp_status_rsvp_updated_at'),
    ]

    operations = [
        migrations.RunPython(rewrite_registration_ids, noop_reverse),
    ]
