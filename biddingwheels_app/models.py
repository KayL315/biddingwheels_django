from django.db import models

# Create your models here.

# User table
class User(models.Model):
    ROLE_CHOICES = [
        ('admin', 'Admin'),
        ('normal', 'Normal'),
    ]
    PAYMENT_METHOD_CHOICES = [
        ('online', 'Online'),
        ('offline', 'Offline'),
    ]

    user_id = models.AutoField(primary_key=True)
    role = models.CharField(max_length=10, choices=ROLE_CHOICES)
    username = models.CharField(max_length=150, unique=True)
    password = models.CharField(max_length=255)
    avatar = models.CharField(max_length=255, blank=True, null=True)
    address = models.CharField(max_length=255, blank=True, null=True)
    payment_method = models.CharField(max_length=10, choices=PAYMENT_METHOD_CHOICES, blank=True, null=True)

    def __str__(self):
        return self.username

    class Meta:
        db_table = 'user'