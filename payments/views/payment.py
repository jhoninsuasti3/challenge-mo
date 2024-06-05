# views/payment.py
from django.db.models import Sum
from rest_framework import status
from rest_framework.authentication import TokenAuthentication
from rest_framework.decorators import (authentication_classes,
                                       permission_classes)
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from payments.models.customer import Customer
from payments.models.loan import Loan
from payments.models.payment import Payment
from payments.serializers.payment import PaymentSerializer


@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated])
class PaymentAPIView(APIView):
    def post(self, request, format=None):
        serializer = PaymentSerializer(data=request.data)
        if serializer.is_valid():
            customer = serializer.validated_data['customer']
            total_debt = customer.loans.filter(status=2).aggregate(
                total_debt=Sum('outstanding'))['total_debt'] or 0

            if total_debt == 0:
                return Response({'error': 'Customer has no active loans'}, status=status.HTTP_400_BAD_REQUEST)

            if serializer.validated_data['total_amount'] > total_debt:
                return Response({'error': 'Payment amount exceeds customer\'s total debt'}, status=status.HTTP_400_BAD_REQUEST)

            payment = serializer.save()

            return Response(PaymentSerializer(payment).data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def get(self, request, customer_external_id, format=None):
        customer = Customer.objects.filter(
            external_id=customer_external_id).first()
        if not customer:
            return Response({'error': 'Cliente no encontrado'}, status=status.HTTP_404_NOT_FOUND)

        payments = Payment.objects.filter(customer=customer)
        serializer = PaymentSerializer(payments, many=True)
        return Response(serializer.data)
