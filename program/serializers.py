from rest_framework import serializers
from .models import Rsvp


class RsvpSerializer(serializers.ModelSerializer):
    class Meta:
        model = Rsvp
        fields = ('name', 'phone_number', 'attending_members', 'attending_children')
        extra_kwargs = {
            'phone_number': {'validators': []},
        }

    def validate_name(self, value):
        name = (value or '').strip()
        if len(name) < 2:
            raise serializers.ValidationError('Please enter a valid name.')
        return name

    def validate_phone_number(self, value):
        digits = ''.join(ch for ch in (value or '') if ch.isdigit())
        if digits.startswith('91') and len(digits) == 12:
            digits = digits[2:]
        if len(digits) != 10:
            raise serializers.ValidationError('Enter a 10 digit phone number.')
        if not digits.isdigit():
            raise serializers.ValidationError('Phone number can contain digits only.')
        phone = f'+91{digits}'
        if Rsvp.objects.filter(phone_number=phone).exists():
            raise serializers.ValidationError('This phone number is already registered.')
        return phone

    def validate_attending_members(self, value):
        if value < 1:
            raise serializers.ValidationError('At least one attending member is required.')
        return value

    def validate_attending_children(self, value):
        if value < 0:
            raise serializers.ValidationError('Children count cannot be negative.')
        return value

    def validate(self, attrs):
        members = attrs.get('attending_members') or 0
        children = attrs.get('attending_children') or 0
        if members + children > 10:
            raise serializers.ValidationError('Only 10 attendees allowed.')
        return attrs
