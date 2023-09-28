from django.db import models

    
class SmsWebhookData(models.Model):
    class CARRIER(models.TextChoices):
        ATT = 'att', 'ATT'
        VERIZON = 'verizon', 'Verizon'
        TMOBILE = 'tmobile', 'TMobile'
        OTHER = 'other', 'Other'
    
    from_number = models.CharField(max_length=10, db_index=True)
    msg_text = models.TextField()
    carrier = models.CharField(max_length=10, choices=CARRIER.choices, default=CARRIER.OTHER)
    response_data = models.TextField(null=True, blank=True)
    added = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"{self.from_number} - {self.added}"
    
    class Meta:
        ordering = ["-added"]
        verbose_name = verbose_name_plural = "SMS Webhook Data (Under Maintenance)"
