# payments/serializers/payment.py

from rest_framework import serializers

from payments.models.payment import Payment, PaymentDetail


class PaymentDetailSerializer(serializers.ModelSerializer):
    class Meta:
        model = PaymentDetail
        fields = ['id', 'payment', 'loan', 'amount']


class PaymentSerializer(serializers.ModelSerializer):
    details = PaymentDetailSerializer(many=True)

    class Meta:
        model = Payment
        fields = ['id', 'external_id', 'total_amount', 'status',
                  'paid_at', 'created_at', 'updated_at', 'customer', 'details']

    def create(self, validated_data):
        details_data = validated_data.pop('details')
        payment = Payment.objects.create(**validated_data)
        for detail_data in details_data:
            PaymentDetail.objects.create(payment=payment, **detail_data)
        return payment
