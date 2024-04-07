from django.db import models

# Create your models here.
class Widget(models.Model):
    name = models.CharField(max_length=140)

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


#Message table
class Message(models.Model):
    sender_id = models.ForeignKey(User, on_delete=models.CASCADE, related_name='sent_messages', db_column='senderID')
    receiver_id = models.ForeignKey(User, on_delete=models.CASCADE, related_name='received_messages', db_column='receiverID')
    description = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"From: {self.sender_id.username}, To: {self.receiver_id.username}, Sent: {self.timestamp}"
    
    class Meta:
        db_table = 'Message'
