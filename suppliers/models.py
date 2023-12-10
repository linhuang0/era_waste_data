from django.db import models

class CUSTOMERS(models.Model):
    customer_name = models.CharField(max_length=128)
    customer_number = models.CharField(max_length=32, unique=True)

    def __str__(self):
        return self.customer_name
