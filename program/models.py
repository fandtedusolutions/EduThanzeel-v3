from django.db import models, transaction
from django.db.models import Count, F, Sum


class Rsvp(models.Model):
    ID_PREFIX = 'ETZL'
    FOOD_SEAT_CAPACITY = 100
    STATUS_PENDING = 'pending'
    STATUS_CONVERTED = 'converted'
    STATUS_CHOICES = [
        (STATUS_PENDING, 'Pending'),
        (STATUS_CONVERTED, 'Converted'),
    ]

    name = models.CharField(max_length=200)
    phone_number = models.CharField(max_length=20, unique=True)
    attending_members = models.PositiveIntegerField(
        help_text='Adults attending, including you. Does not include children.',
    )
    attending_children = models.PositiveIntegerField(default=0)
    registration_id = models.CharField(max_length=20, unique=True, editable=False)
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default=STATUS_PENDING,
    )
    food_batch = models.PositiveIntegerField(
        null=True,
        blank=True,
        help_text='Food batch number (100 seats each). Set when converted.',
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f'{self.registration_id} — {self.name}'

    @property
    def total_attending(self):
        return self.attending_members + self.attending_children

    @classmethod
    def batch_seat_usage(cls, batch_number, exclude_pk=None):
        qs = cls.objects.filter(status=cls.STATUS_CONVERTED, food_batch=batch_number)
        if exclude_pk:
            qs = qs.exclude(pk=exclude_pk)
        totals = qs.aggregate(
            members=Sum('attending_members'),
            children=Sum('attending_children'),
            families=Count('id'),
        )
        used = (totals['members'] or 0) + (totals['children'] or 0)
        return {
            'batch': batch_number,
            'capacity': cls.FOOD_SEAT_CAPACITY,
            'used': used,
            'remaining': max(cls.FOOD_SEAT_CAPACITY - used, 0),
            'families': totals['families'] or 0,
            'is_full': used >= cls.FOOD_SEAT_CAPACITY,
        }

    @classmethod
    def find_batch_for_seats(cls, seats_needed, exclude_pk=None):
        """Return the earliest batch that can fit seats_needed, or next new batch."""
        batch_numbers = list(
            cls.objects.filter(status=cls.STATUS_CONVERTED, food_batch__isnull=False)
            .exclude(pk=exclude_pk)
            .values_list('food_batch', flat=True)
            .distinct()
            .order_by('food_batch')
        )
        if not batch_numbers:
            batch_numbers = [1]

        for batch_number in batch_numbers:
            usage = cls.batch_seat_usage(batch_number, exclude_pk=exclude_pk)
            if seats_needed <= usage['remaining']:
                return batch_number, usage

        next_batch = max(batch_numbers) + 1
        return next_batch, {
            'batch': next_batch,
            'capacity': cls.FOOD_SEAT_CAPACITY,
            'used': 0,
            'remaining': cls.FOOD_SEAT_CAPACITY,
            'families': 0,
            'is_full': False,
        }

    @classmethod
    def assign_food_batch(cls, lead):
        batch_number, usage = cls.find_batch_for_seats(lead.total_attending, exclude_pk=lead.pk)
        lead.food_batch = batch_number
        return batch_number, usage

    @classmethod
    def family_size_counts(cls, queryset=None):
        qs = queryset if queryset is not None else cls.objects.filter(status=cls.STATUS_CONVERTED)
        qs = qs.annotate(party_size=F('attending_members') + F('attending_children'))
        counts = {size: 0 for size in range(1, 6)}
        for row in qs.values('party_size').annotate(total=Count('id')):
            size = row['party_size']
            if size in counts:
                counts[size] = row['total']
        return counts

    @classmethod
    def all_food_batches(cls):
        converted = cls.objects.filter(status=cls.STATUS_CONVERTED, food_batch__isnull=False)
        batch_numbers = list(
            converted.values_list('food_batch', flat=True).distinct().order_by('food_batch')
        )
        if not batch_numbers:
            batch_numbers = [1]

        batches = []
        for batch_number in batch_numbers:
            families = list(
                converted.filter(food_batch=batch_number).order_by('created_at', 'id')
            )
            usage = cls.batch_seat_usage(batch_number)
            progress = 0
            if usage['capacity']:
                progress = min(round((usage['used'] / usage['capacity']) * 100), 100)
            batches.append({
                **usage,
                'progress': progress,
                'families_list': families,
                'size_counts': cls.family_size_counts(
                    cls.objects.filter(status=cls.STATUS_CONVERTED, food_batch=batch_number)
                ),
            })
        return batches

    @classmethod
    def next_registration_id(cls):
        ids = cls.objects.filter(registration_id__startswith=cls.ID_PREFIX).values_list(
            'registration_id', flat=True
        )
        numbers = [int(''.join(ch for ch in value if ch.isdigit()) or 0) for value in ids]
        number = max(numbers) if numbers else 0
        return f'{cls.ID_PREFIX}{number + 1:02d}'

    def save(self, *args, **kwargs):
        if not self.registration_id:
            with transaction.atomic():
                self.registration_id = self.next_registration_id()
                return super().save(*args, **kwargs)
        return super().save(*args, **kwargs)
