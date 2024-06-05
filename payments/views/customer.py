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
from payments.serializers.customer import CustomerSerializer


@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated])
class CustomerAPIView(APIView):
    def post(self, request, format=None):
        serializer = CustomerSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def get(self, request, format=None):
        paginator = PageNumberPagination()
        paginator.page_size = 10
        customers = Customer.objects.all()
        result_page = paginator.paginate_queryset(customers, request)
        serializer = CustomerSerializer(result_page, many=True)
        return paginator.get_paginated_response(serializer.data)

    def get_balance(self, customer):
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
    pass
