from django.contrib import admin
from .models import UserAccountModel,UserAddressModel
# Register your models here.
admin.site.register(UserAddressModel)
admin.site.register(UserAccountModel)