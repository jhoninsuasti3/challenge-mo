from rest_framework import serializers

from payments.models.loan import Loan


class LoanSerializer(serializers.ModelSerializer):
    """
    Serializer for loans, handling all fields of the Loan model.

    This serializer handles the creation of a loan instance and ensures that the
    'outstanding' field is set to the 'amount' field during creation.
    """

    class Meta:
        model = Loan
        fields = '__all__'

    def create(self, validated_data):
        """
        Create a new loan instance and set the outstanding amount.

        Parameters:
            validated_data: Validated data for creating the loan.

        Returns:
            loan: The created Loan instance.
        """
        loan = Loan.objects.create(**validated_data)
        loan.outstanding = validated_data['amount']
        loan.save()
        return loan
