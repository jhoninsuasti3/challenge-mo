# serializers/payment.py
from django.db.models import Sum
from rest_framework import serializers

from payments.models import Customer, Loan, Payment, PaymentDetail


class PaymentDetailSerializer(serializers.ModelSerializer):
    loan_external_id = serializers.CharField(write_only=True)

    class Meta:
        model = PaymentDetail
        fields = ['loan_external_id', 'amount']


class PaymentSerializer(serializers.ModelSerializer):
    details = PaymentDetailSerializer(many=True)
    customer_external_id = serializers.CharField(write_only=True)

    class Meta:
        model = Payment
        fields = ['external_id', 'total_amount',
                  'status', 'customer_external_id', 'details']

    def validate(self, data):
        customer_external_id = data.get('customer_external_id')
        try:
            customer = Customer.objects.get(external_id=customer_external_id)
        except Customer.DoesNotExist:
            raise serializers.ValidationError(
                {'customer_external_id': 'Customer does not exist'})

        # Verificar si el pago no excede la deuda total del cliente
        total_debt = customer.loans.filter(status__in=[1, 2]).aggregate(
            Sum('outstanding'))['outstanding__sum'] or 0
        print(f"------- Total Debt: {total_debt}")
        if data['total_amount'] > total_debt:
            raise serializers.ValidationError(
                {'total_amount': 'Payment amount exceeds customer\'s total debt'})

        return data

    def create(self, validated_data):
        details_data = validated_data.pop('details')
        customer_external_id = validated_data.pop('customer_external_id')
        customer = Customer.objects.get(external_id=customer_external_id)

        payment = Payment.objects.create(customer=customer, **validated_data)
        for detail_data in details_data:
            loan_external_id = detail_data.pop('loan_external_id')
            loan = Loan.objects.get(external_id=loan_external_id)
            PaymentDetail.objects.create(
                payment=payment, loan=loan, **detail_data)

        # Actualizar los préstamos después de guardar el pago
        payment.update_loans()
        return payment
