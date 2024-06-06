# payments/urls.py
from django.urls import path

from payments.views import customer, loan, payment

urlpatterns = [
    # Customers
    path('api/customers/', customer.CustomerAPIView.as_view(),
         name='customer-list-create'),
    path('api/customers/bulk-upload/', customer.CustomerUploadAPIView.as_view(),
         name='customer-bulk-upload'),
    # Loans
    path('api/loans/', loan.LoanAPIView.as_view(), name='loan-list-create'),
    path('api/loans/activate/',
         loan.ActivateLoanAPIView.as_view(), name='activate_loan'),

    path('api/loans/<str:customer_external_id>/',
         loan.LoansByCustomerAPIView.as_view(), name='loans_by_customer'),

    # Payments
    path('api/payment/', payment.PaymentAPIView.as_view(), name='create_payment'),
    path('api/payment/customer/<str:customer_external_id>/',
         payment.PaymentAPIView.as_view(), name='payments_by_customer'),
]
