# models/loan.py
from django.db import models
from django.db.models import Sum
from django.utils import timezone

from payments.models.customer import Customer


class Loan(models.Model):
    STATUS_CHOICES = (
        (1, 'pending'),
        (2, 'active'),
        (3, 'rejected'),
        (4, 'paid'),
    )

    external_id = models.CharField(max_length=60, unique=True)
    amount = models.DecimalField(max_digits=12, decimal_places=2)
    contract_version = models.CharField(max_length=30, blank=True, null=True)
    status = models.SmallIntegerField(choices=STATUS_CHOICES, default=1)
    outstanding = models.DecimalField(
        max_digits=12, decimal_places=2, default=0)
    taken_at = models.DateTimeField(null=True, blank=True)
    maximum_payment_date = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    customer = models.ForeignKey(
        Customer, related_name='loans', on_delete=models.CASCADE)

    def save(self, *args, **kwargs):
        if self.status == 2 and not self.taken_at:
            self.taken_at = timezone.now()
        super().save(*args, **kwargs)

    def clean(self):
        if self.status == 2 and self.outstanding == 0:
            self.status = 4
        super().clean()

    def __str__(self):
        return self.external_id
