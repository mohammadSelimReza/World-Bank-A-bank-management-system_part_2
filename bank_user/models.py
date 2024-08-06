from django.db import models
from django.contrib.auth.models import User

class UserAccountModel(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='account')
    account_type = models.CharField(max_length=50)
    gender = models.CharField(max_length=10)
    birth_date = models.DateField()
    account_no = models.BigIntegerField()
    balance = models.DecimalField(default=0,decimal_places=2,max_digits=12)
    
class UserAddressModel(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='address')
    street_address = models.CharField(max_length=100)
    city = models.CharField(max_length=100)
    postal_code = models.CharField(max_length=10)
    country = models.CharField(max_length=100)
