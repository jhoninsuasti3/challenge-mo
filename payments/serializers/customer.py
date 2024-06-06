import random

from django.utils import timezone
from rest_framework import serializers

from payments.models.customer import Customer
from payments.models.loan import Loan


class CustomerSerializer(serializers.ModelSerializer):
    """
    Serializer for Customer model, handling the creation and serialization of customer instances.

    Fields:
        - id (int): Unique identifier for the customer.
        - external_id (str): External identifier for the customer.
        - status (int): Status of the customer.
        - score (float): Credit score of the customer.
        - preapproved_at (datetime): Timestamp when the customer was preapproved. This field is read-only.
    """

    class Meta:
        model = Customer
        fields = ['id', 'external_id', 'status', 'score', 'preapproved_at']
        read_only_fields = ['preapproved_at']

    def create(self, validated_data):
        """
        Create a new customer instance with a randomly generated score if not provided.

        Parameters:
            validated_data (dict): Data validated by the serializer.

        Returns:
            Customer: The created Customer instance.
        """
        if 'score' not in validated_data:
            validated_data['score'] = random.randint(1, 100)

        validated_data['preapproved_at'] = timezone.now()

        return super().create(validated_data)


class CustomerBalanceSerializer(serializers.ModelSerializer):
    """
    Serializer for representing a customer's balance and total debt.

    Fields:
        - external_id (str): External identifier for the customer.
        - score (float): Credit score of the customer.
    """

    external_id = serializers.CharField()
    score = serializers.FloatField()

    class Meta:
        model = Customer
        fields = ['external_id', 'score']

    def to_representation(self, instance):
        """
        Customize the representation of the customer instance to include balance and debt information.

        Parameters:
            instance (Customer): The customer instance being serialized.

        Returns:
            dict: A dictionary containing the external_id, score, available amount, and total debt of the customer.
        """
        loans = Loan.objects.filter(customer=instance)
        total_debt = sum(loan.outstanding for loan in loans)
        available_amount = instance.score - total_debt

        return {
            'external_id': instance.external_id,
            'score': instance.score,
            'available_amount': available_amount,
            'total_debt': total_debt
        }
