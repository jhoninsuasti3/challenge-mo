from django.db.models import Sum
from rest_framework import status
from rest_framework.authentication import TokenAuthentication
from rest_framework.decorators import (authentication_classes,
                                       permission_classes)
from rest_framework.pagination import PageNumberPagination
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from payments.models.customer import Customer
from payments.serializers.customer import (CustomerBalanceSerializer,
                                           CustomerSerializer)


@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated])
class CustomerAPIView(APIView):
    """
    API endpoint for creating, retrieving customers and calculating their balance.

    Methods:
        post: Create a new customer.
        get: Retrieve all customers with pagination.
        get_balance: Calculate and return the balance of a customer.
    """

    def post(self, request, format=None):
        """
        Create a new customer.

        Parameters:
            request: HTTP request.
            format: Format suffix.

        Returns:
            Response: HTTP response with created customer data or errors if validation fails.
        """

        serializer = CustomerSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def get(self, request, format=None):
        """
        Retrieve all customers with pagination.

        Parameters:
            request: HTTP request.
            format: Format suffix.

        Returns:
            Response: Paginated HTTP response with customer data.
        """

        paginator = PageNumberPagination()
        paginator.page_size = 10
        customers = Customer.objects.all()
        result_page = paginator.paginate_queryset(customers, request)
        serializer = CustomerSerializer(result_page, many=True)
        return paginator.get_paginated_response(serializer.data)

    def get_balance(self, customer):
        """
        Calculate and return the balance of a customer.

        Parameters:
            customer: Customer instance.

        Returns:
            dict: A dictionary with total debt and available amount.
        """

        total_debt = customer.loans.filter(status__in=['pending', 'active']).aggregate(
            total_debt=Sum('outstanding'))['total_debt'] or 0
        available_amount = customer.score - total_debt
        return {
            'total_debt': total_debt,
            'available_amount': available_amount
        }


@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated])
class CustomerUploadAPIView(APIView):
    """
    API endpoint for uploading customer data.

    Methods:
        pass: Currently not implemented.
    """
    pass


@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated])
class CustomerBalanceAPIView(APIView):
    """
    API endpoint for retrieving the balance of all customers.

    Methods:
        get: Retrieve the balance of all customers.
    """

    def get(self, request, format=None):
        """
        Retrieve the balance of all customers.

        Parameters:
            request: HTTP request.
            format: Format suffix.

        Returns:
            Response: HTTP response with customer balance data.
        """

        customers = Customer.objects.all()
        serializer = CustomerBalanceSerializer(customers, many=True)
        return Response(serializer.data)
