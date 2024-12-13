from django.db import models
from django.contrib.auth.models import AbstractUser
from phonenumber_field.modelfields import PhoneNumberField


class CustomUser(AbstractUser): # Номер телефона
    phone = PhoneNumberField(
        unique=True, null=True, blank=False,
        error_messages={
        'unique': "Этот номер телефона уже зарегистрирован.",  
        }
    )  
    balance = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)  # Баланс (вымышленная валюта)
    username = models.CharField(max_length=255, unique=False, blank=True, null=True)
    
    USERNAME_FIELD = 'phone'
    def __str__(self):
        return f"{self.last_name} {self.first_name} ({self.phone})"

class Transaction(models.Model):
    sender = models.ForeignKey(CustomUser, related_name='sent_transactions', on_delete=models.CASCADE)
    recipient = models.ForeignKey(CustomUser, related_name='received_transactions', on_delete=models.CASCADE)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.sender} отправил {self.amount} {self.recipient}"