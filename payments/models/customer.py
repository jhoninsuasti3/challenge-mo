# payments/models/customer.py

import uuid

from django.db import models


class Customer(models.Model):
    STATUS_CHOICES = [
        (1, 'Activo'),
        (2, 'Inactivo'),
    ]

    external_id = models.UUIDField(
        default=uuid.uuid4, editable=False, unique=True)
    status = models.PositiveSmallIntegerField(choices=STATUS_CHOICES)
    score = models.DecimalField(max_digits=12, decimal_places=2)
    preapproved_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return str(self.external_id)
