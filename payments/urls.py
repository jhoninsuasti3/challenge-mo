# payments/urls.py
from django.urls import path

from payments.views import customer, loan, payment

urlpatterns = [
    # Customers
    path('customers/', customer.CustomerAPIView.as_view(),
         name='customer-list-create'),
    path('customers/bulk-upload/', customer.CustomerUploadAPIView.as_view(),
         name='customer-bulk-upload'),
    # Loans
    path('loans/', loan.LoanAPIView.as_view(), name='loan-list-create'),
    path('loans/<str:customer_external_id>/',
         loan.LoansByCustomerAPIView.as_view(), name='loans_by_customer'),

    # Payments
    path('payments/', payment.PaymentAPIView.as_view(), name='create_payment'),
    path('payments/customer/<str:customer_external_id>/',
         payment.PaymentAPIView.as_view(), name='payments_by_customer'),
]
