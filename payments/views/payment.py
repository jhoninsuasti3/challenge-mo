# views/payment.py
from django.utils import timezone
from rest_framework import serializers, status
from rest_framework.authentication import TokenAuthentication
from rest_framework.decorators import (authentication_classes,
                                       permission_classes)
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from payments.models import Loan, Payment, PaymentDetail
from payments.serializers.payment import PaymentSerializer


@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated])
class PaymentAPIView(APIView):

    def post(self, request, format=None):
        serializer = PaymentSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def get(self, request, customer_external_id, format=None):
        payments = Payment.objects.filter(
            customer__external_id=customer_external_id)
        serializer = PaymentSerializer(payments, many=True)
        return Response(serializer.data)
