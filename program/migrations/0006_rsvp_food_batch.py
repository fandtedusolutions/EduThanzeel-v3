from django.db import migrations, models


def assign_existing_batches(apps, schema_editor):
    Rsvp = apps.get_model('program', 'Rsvp')
    capacity = 100
    batch = 1
    used = 0
    for lead in Rsvp.objects.filter(status='converted').order_by('created_at', 'id'):
        seats = (lead.attending_members or 0) + (lead.attending_children or 0)
        if seats <= 0:
            seats = 1
        if used > 0 and used + seats > capacity:
            batch += 1
            used = 0
        lead.food_batch = batch
        lead.save(update_fields=['food_batch'])
        used += seats


def clear_batches(apps, schema_editor):
    Rsvp = apps.get_model('program', 'Rsvp')
    Rsvp.objects.update(food_batch=None)


class Migration(migrations.Migration):

    dependencies = [
        ('program', '0005_rewrite_registration_id_etzl'),
    ]

    operations = [
        migrations.AddField(
            model_name='rsvp',
            name='food_batch',
            field=models.PositiveIntegerField(
                blank=True,
                help_text='Food batch number (100 seats each). Set when converted.',
                null=True,
            ),
        ),
        migrations.RunPython(assign_existing_batches, clear_batches),
    ]
