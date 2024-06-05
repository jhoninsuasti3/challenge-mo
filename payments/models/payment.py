# models/payment.py
from django.db import models
from django.utils import timezone

from .customer import Customer
from .loan import Loan


class Payment(models.Model):
    STATUS_CHOICES = (
        (1, 'completed'),
        (2, 'rejected'),
    )

    external_id = models.CharField(max_length=60, unique=True)
    total_amount = models.DecimalField(max_digits=20, decimal_places=2)
    status = models.SmallIntegerField(choices=STATUS_CHOICES, default=1)
    paid_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    customer = models.ForeignKey(
        Customer, related_name='payments', on_delete=models.CASCADE)

    def save(self, *args, **kwargs):
        if self.status == 1:
            self.paid_at = timezone.now()
        super().save(*args, **kwargs)

        if self.status == 1:
            self.update_loans()

    def update_loans(self):
        remaining_amount = self.total_amount
        loans = Loan.objects.filter(
            customer=self.customer, status=2).order_by('created_at')

        payment_details = []

        for loan in loans:
            if remaining_amount <= 0:
                break

            detail_amount = min(loan.outstanding, remaining_amount)
            payment_details.append(PaymentDetail(
                payment=self, loan=loan, amount=detail_amount))

            remaining_amount -= detail_amount
            loan.outstanding -= detail_amount

            if loan.outstanding == 0:
                loan.status = 4  # paid
            loan.save()

        PaymentDetail.objects.bulk_create(payment_details)

        if remaining_amount > 0:
            raise ValueError("Payment exceeds outstanding debt")


class PaymentDetail(models.Model):
    payment = models.ForeignKey(
        Payment, related_name='details', on_delete=models.CASCADE)
    loan = models.ForeignKey(
        Loan, related_name='payment_details', on_delete=models.CASCADE)
    amount = models.DecimalField(max_digits=20, decimal_places=2)
