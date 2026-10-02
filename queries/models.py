from django.db import models

class Query(models.Model):
    date = models.DateField()
    fc_id_name = models.CharField(max_length=150)
    description = models.TextField()

    SYSTEM_CHOICES = [
        ('Biometric Device', 'Biometric Device'),
        ('YDL CRM', 'YDL CRM'),
    ]
    related_system = models.CharField(max_length=50, choices=SYSTEM_CHOICES)

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.fc_id_name


class Functionality(models.Model):
    date = models.DateField()
    fc_id_name = models.CharField(max_length=150)
    description = models.TextField()  # multi-line

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.fc_id_name
