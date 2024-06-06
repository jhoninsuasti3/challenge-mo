# views/payment.py
from rest_framework import serializers, status
from rest_framework.authentication import TokenAuthentication
from rest_framework.decorators import (authentication_classes,
                                       permission_classes)
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from payments.models import Payment
from payments.serializers.payment import PaymentSerializer


@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated])
class PaymentAPIView(APIView):

    def post(self, request, format=None):
        print(request.data)
        serializer = PaymentSerializer(data=request.data)
        if serializer.is_valid():
            try:
                print("Antes del payment|")
                payment = serializer.save()
                print("Despues del payment|------")
                return Response(PaymentSerializer(payment).data, status=status.HTTP_201_CREATED)
            except serializers.ValidationError as e:
                return Response(e.detail, status=status.HTTP_400_BAD_REQUEST)
            except ValueError as e:
                return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def get(self, request, format=None):
        payments = Payment.objects.all()
        serializer = PaymentSerializer(payments, many=True)
        return Response(serializer.data)
