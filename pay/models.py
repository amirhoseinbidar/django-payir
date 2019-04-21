from django.db import models
from django.conf import settings
import uuid

class TransactionBase(models.Model):
    uuid_id = models.UUIDField(
        primary_key=True, default=uuid.uuid4, editable=False, max_length=16)
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, blank=True, null=True)
    trans_id = models.CharField(unique=True, max_length=31)
    factor_number = models.CharField(max_length=31, blank=True)
    card_number = models.CharField(max_length=16)
    timestamp = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True

class UserTransaction(TransactionBase):
    pass
