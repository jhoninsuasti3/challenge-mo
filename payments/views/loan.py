# views/loan.py
from django.db.models import Sum
from django.utils import timezone
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
    """
    API endpoint for creating, retrieving, updating loans.

    Methods:
        post: Create a new loan.
        get: Retrieve all loans.
        put: Update an existing loan.
    """

    def post(self, request, format=None):
        """
        Create a new loan.

        Parameters:
            request: HTTP request.
            format: Format suffix.

        Returns:
            Response: HTTP response.

        Raises:
            Response: HTTP response if validation fails or if loan amount exceeds customer's credit limit.
        """

        serializer = LoanSerializer(data=request.data)
        if serializer.is_valid():
            customer = serializer.validated_data['customer']
            total_debt = customer.loans.filter(status__in=[1, 2]).aggregate(
                Sum('outstanding'))['outstanding__sum'] or 0
            if total_debt + serializer.validated_data['amount'] > customer.score:
                return Response({'error': 'Loan amount exceeds customer\'s credit limit'}, status=status.HTTP_400_BAD_REQUEST)

            serializer.save()

            customer_external_id = customer.external_id

            response_data = serializer.data
            response_data['customer_external_id'] = customer_external_id

            return Response(response_data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def get(self, request, format=None):
        """
        Retrieve all loans.

        Parameters:
            request: HTTP request.
            format: Format suffix.

        Returns:
            Response: HTTP response.
        """

        loans = Loan.objects.all()
        serializer = LoanSerializer(loans, many=True)
        return Response(serializer.data)

    def put(self, request, pk, format=None):
        """
        Update an existing loan.

        Parameters:
            request: HTTP request.
            pk: Loan primary key.
            format: Format suffix.

        Returns:
            Response: HTTP response.

        Raises:
            Response: HTTP response if loan is not found or if validation fails.
        """

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
    """
    API endpoint for retrieving loans by customer.

    Methods:
        get: Retrieve loans associated with a specific customer.
    """

    def get(self, request, customer_external_id, format=None):
        """
        Retrieve loans associated with a specific customer.

        Parameters:
            request: HTTP request.
            customer_external_id: External ID of the customer.
            format: Format suffix.

        Returns:
            Response: HTTP response.

        Raises:
            Response: HTTP response if customer is not found.
        """

        customer = Customer.objects.filter(
            external_id=customer_external_id).first()
        if not customer:
            return Response({'error': 'Customer not found'}, status=status.HTTP_404_NOT_FOUND)

        loans = Loan.objects.filter(customer=customer)

        serializer = LoanSerializer(loans, many=True)

        return Response(serializer.data)


class ActivateLoanAPIView(APIView):
    """
    API endpoint for activating a loan.

    Methods:
        put: Activate a loan.
    """

    def put(self, request, format=None):
        """
        Activate a loan.

        Parameters:
            request: HTTP request.
            format: Format suffix.

        Returns:
            Response: HTTP response.
        """

        external_id = request.data.get('external_id')
        if external_id:
            try:
                # Filter by 'pending' status
                loan = Loan.objects.get(external_id=external_id, status=1)
                loan.status = 2  # Change status to 'active'
                loan.taken_at = timezone.now()  # Update 'taken_at' date
                loan.save()  # Save changes to the database
                return Response({'message': 'Loan activated successfully'}, status=status.HTTP_200_OK)
            except Loan.DoesNotExist:
                return Response({'error': 'Loan not found or already activated'}, status=status.HTTP_404_NOT_FOUND)
        else:
            return Response({'error': 'External ID not provided'}, status=status.HTTP_400_BAD_REQUEST)
