# serializers/loan.py
from rest_framework import serializers

from payments.models.loan import Loan


class LoanSerializer(serializers.ModelSerializer):
    class Meta:
        model = Loan
        fields = '__all__'

    def create(self, validated_data):
        loan = Loan.objects.create(**validated_data)
        loan.outstanding = validated_data['amount']
        loan.save()
        return loan
