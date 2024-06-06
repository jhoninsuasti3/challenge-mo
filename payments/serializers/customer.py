import random

from django.utils import timezone
from rest_framework import serializers

from payments.models.customer import Customer
from payments.models.loan import Loan


class CustomerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Customer
        fields = ['id', 'external_id', 'status', 'score', 'preapproved_at']
        read_only_fields = ['preapproved_at']

    def create(self, validated_data):
        if 'score' not in validated_data:
            validated_data['score'] = random.randint(1, 100.000)

        validated_data['preapproved_at'] = timezone.now()

        return super().create(validated_data)


class CustomerBalanceSerializer(serializers.ModelSerializer):
    external_id = serializers.CharField()
    score = serializers.FloatField()

    class Meta:
        model = Customer
        fields = ['external_id', 'score']

    def to_representation(self, instance):
        loans = Loan.objects.filter(customer=instance)
        total_debt = sum(loan.outstanding for loan in loans)
        available_amount = instance.score - total_debt

        return {
            'external_id': instance.external_id,
            'score': instance.score,
            'available_amount': available_amount,
            'total_debt': total_debt
        }
