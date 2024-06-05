import random

from django.utils import timezone
from rest_framework import serializers

from payments.models.customer import Customer


class CustomerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Customer
        fields = ['id', 'external_id', 'status', 'score', 'preapproved_at']
        read_only_fields = ['preapproved_at']

    def create(self, validated_data):
        if 'score' not in validated_data:
            validated_data['score'] = random.randint(1, 100)

        validated_data['preapproved_at'] = timezone.now()

        return super().create(validated_data)
