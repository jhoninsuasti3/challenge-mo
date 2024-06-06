from rest_framework import status
from rest_framework.authentication import TokenAuthentication
from rest_framework.decorators import (authentication_classes,
                                       permission_classes)
from rest_framework.pagination import PageNumberPagination
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from payments.models import Payment
from payments.serializers.payment import PaymentSerializer


@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated])
class PaymentAPIView(APIView):
    """
    View to handle the creation and retrieval of payments.

    Supported methods:
    - POST: Create a new payment.
    - GET: Get a paginated list of payments associated with an external customer.

    Requires authentication and token permissions.
    """

    def post(self, request, format=None):
        """
        Create a new payment.

        Parameters:
        - request: HttpRequest object.
        - format: Format of the request.

        Returns:
        - HTTP response with the operation status.
        """
        serializer = PaymentSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def get(self, request, customer_external_id, format=None):
        """
        Get a paginated list of payments associated with an external customer.

        Parameters:
        - request: HttpRequest object.
        - customer_external_id: External ID of the customer.
        - format: Format of the request.

        Returns:
        - HTTP response with the paginated list of payments.
        """
        # Get payments associated with the external customer
        payments = Payment.objects.filter(
            customer__external_id=customer_external_id)

        # Paginate the results
        paginator = PageNumberPagination()
        paginator.page_size = 10  # You can adjust this as per your needs

        paginated_payments = paginator.paginate_queryset(payments, request)
        serializer = PaymentSerializer(paginated_payments, many=True)

        return paginator.get_paginated_response(serializer.data)
