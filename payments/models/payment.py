# models/payment.py
from django.db import models
from django.utils import timezone

from payments.models import Customer, Loan


class Payment(models.Model):
    STATUS_CHOICES = (
        (1, 'completed'),
        (2, 'rejected'),
    )

    external_id = models.CharField(max_length=60, unique=True)
    total_amount = models.DecimalField(max_digits=20, decimal_places=10)
    status = models.SmallIntegerField(choices=STATUS_CHOICES, default=1)
    paid_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    customer = models.ForeignKey(
        Customer, related_name='payments', on_delete=models.CASCADE)

    def __str__(self):
        return self.external_id

    def save(self, *args, **kwargs):
        if self.status == 1 and not self.paid_at:
            self.paid_at = timezone.now()
        super().save(*args, **kwargs)

    def update_loans(self):
        remaining_amount = self.total_amount
        print("////////////////")
        print(remaining_amount)
        loans = Loan.objects.filter(
            customer=self.customer, status=2).order_by('created_at')
        from pprint import pprint
        pprint(loans)
        for loan in loans:
            if remaining_amount <= 0:
                break

            if remaining_amount >= loan.outstanding:
                remaining_amount -= loan.outstanding
                loan.outstanding = 0
                loan.status = 4  # paid
            else:
                loan.outstanding -= remaining_amount
                remaining_amount = 0

            loan.save()

        if remaining_amount > 0:
            raise ValueError("Payment exceeds outstanding debt")


class PaymentDetail(models.Model):
    payment = models.ForeignKey(
        Payment, related_name='details', on_delete=models.CASCADE)
    loan = models.ForeignKey(
        Loan, related_name='payment_details', on_delete=models.CASCADE)
    amount = models.DecimalField(max_digits=20, decimal_places=2)
