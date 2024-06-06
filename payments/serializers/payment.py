from django.db.models import Sum
from rest_framework import serializers

from payments.models import Customer, Loan, Payment, PaymentDetail


class PaymentDetailSerializer(serializers.ModelSerializer):
    """
    Serializer for payment details, including loan external ID and amount.

    Fields:
        loan_external_id: External ID of the loan (write-only).
        amount: Amount of the payment detail.
    """

    loan_external_id = serializers.CharField(write_only=True)

    class Meta:
        model = PaymentDetail
        fields = ['loan_external_id', 'amount']


class PaymentSerializer(serializers.ModelSerializer):
    """
    Serializer for payments, including details and customer information.

    Fields:
        external_id: External ID of the payment.
        total_amount: Total amount of the payment.
        status: Status of the payment.
        customer_external_id: External ID of the customer (write-only).
        details: List of payment details.
    """

    details = PaymentDetailSerializer(many=True)
    customer_external_id = serializers.CharField(write_only=True)

    class Meta:
        model = Payment
        fields = ['external_id', 'total_amount',
                  'status', 'customer_external_id', 'details']

    def validate(self, data):
        """
        Validate the payment data to ensure the customer exists and the payment amount does not exceed the customer's total debt.

        Parameters:
            data: Dictionary containing payment data.

        Returns:
            data: Validated payment data.

        Raises:
            serializers.ValidationError: If the customer does not exist or the payment amount exceeds the customer's total debt.
        """

        customer_external_id = data.get('customer_external_id')
        try:
            customer = Customer.objects.get(external_id=customer_external_id)
        except Customer.DoesNotExist:
            raise serializers.ValidationError(
                {'customer_external_id': 'Customer does not exist'})

        total_debt = customer.loans.filter(status__in=[1, 2]).aggregate(
            Sum('outstanding'))['outstanding__sum'] or 0
        if data['total_amount'] > total_debt:
            raise serializers.ValidationError(
                {'total_amount': 'Payment amount exceeds customer\'s total debt'})

        return data

    def create(self, validated_data):
        """
        Create a new payment and its related payment details.

        Parameters:
            validated_data: Validated payment data.

        Returns:
            payment: The created Payment instance.
        """

        details_data = validated_data.pop('details')
        customer_external_id = validated_data.pop('customer_external_id')
        customer = Customer.objects.get(external_id=customer_external_id)

        payment = Payment.objects.create(customer=customer, **validated_data)
        for detail_data in details_data:
            loan_external_id = detail_data.pop('loan_external_id')
            loan = Loan.objects.get(external_id=loan_external_id)
            PaymentDetail.objects.create(
                payment=payment, loan=loan, **detail_data)

        # Update loans after saving the payment
        payment.update_loans()
        return payment
