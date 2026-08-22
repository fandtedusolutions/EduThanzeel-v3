from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('program', '0006_rsvp_food_batch'),
    ]

    operations = [
        migrations.AddField(
            model_name='rsvp',
            name='whatsapp_sent_at',
            field=models.DateTimeField(
                blank=True,
                help_text='When the pass WhatsApp message was sent from the dashboard.',
                null=True,
            ),
        ),
    ]
