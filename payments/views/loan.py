# views/loan.py
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
from payments.serializers.loan import LoanSerializer


@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated])
class LoanAPIView(APIView):
    def post(self, request, format=None):
        serializer = LoanSerializer(data=request.data)
        if serializer.is_valid():
            customer = serializer.validated_data['customer']
            total_debt = customer.loans.filter(status__in=[1, 2]).aggregate(
                Sum('outstanding'))['outstanding__sum'] or 0
            if total_debt + serializer.validated_data['amount'] > customer.score:
                return Response({'error': 'El monto del préstamo supera el límite de crédito disponible del cliente'}, status=status.HTTP_400_BAD_REQUEST)

            serializer.save()

            customer_external_id = customer.external_id

            response_data = serializer.data
            response_data['customer_external_id'] = customer_external_id

            return Response(response_data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def get(self, request, format=None):
        loans = Loan.objects.all()
        serializer = LoanSerializer(loans, many=True)
        return Response(serializer.data)

    def put(self, request, pk, format=None):
        try:
            loan = Loan.objects.get(pk=pk)
        except Loan.DoesNotExist:
            return Response({'error': 'Loan not found'}, status=status.HTTP_404_NOT_FOUND)

        serializer = LoanSerializer(loan, data=request.data, partial=True)
        if serializer.is_valid():
            updated_loan = serializer.save()
            return Response(LoanSerializer(updated_loan).data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated])
class LoansByCustomerAPIView(APIView):
    def get(self, request, customer_external_id, format=None):

        customer = Customer.objects.filter(
            external_id=customer_external_id).first()
        if not customer:
            return Response({'error': 'Cliente no encontrado'}, status=status.HTTP_404_NOT_FOUND)

        loans = Loan.objects.filter(customer=customer)

        serializer = LoanSerializer(loans, many=True)

        return Response(serializer.data)
