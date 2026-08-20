from django.db import models, transaction


class Rsvp(models.Model):
    ID_PREFIX = 'TKMK'

    name = models.CharField(max_length=200)
    phone_number = models.CharField(max_length=20, unique=True)
    attending_members = models.PositiveIntegerField(
        help_text='Adults attending, including you. Does not include children.',
    )
    attending_children = models.PositiveIntegerField(default=0)
    registration_id = models.CharField(max_length=20, unique=True, editable=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f'{self.registration_id} — {self.name}'

    @property
    def total_attending(self):
        return self.attending_members + self.attending_children

    @classmethod
    def next_registration_id(cls):
        ids = cls.objects.filter(registration_id__startswith=cls.ID_PREFIX).values_list(
            'registration_id', flat=True
        )
        numbers = [int(''.join(ch for ch in value if ch.isdigit()) or 0) for value in ids]
        number = max(numbers) if numbers else 0
        return f'{cls.ID_PREFIX}{number + 1:03d}'

    def save(self, *args, **kwargs):
        if not self.registration_id:
            with transaction.atomic():
                self.registration_id = self.next_registration_id()
                return super().save(*args, **kwargs)
        return super().save(*args, **kwargs)
