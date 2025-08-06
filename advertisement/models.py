import random
import string
from django.db import models
from django.db.models.signals import pre_save
from django.dispatch import receiver
from django.contrib.auth import get_user_model
User = get_user_model()


class Advertisement(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='advertisements')
    title = models.TextField(blank=True, null=True)
    description = models.TextField(blank=True, null=True)
    category = models.TextField(blank=True, null=True)
    views = models.PositiveIntegerField(default=0)
    url = models.URLField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    status = models.CharField(
        max_length=500,
        choices=[('pending', 'Pending'), ('approved', 'Approved'), ('rejected', 'Rejected')],
        default='pending'
    )
    serial_number = models.CharField(max_length=5, unique=True, editable=False)

    class Meta:
        verbose_name = "Advertisement"
        verbose_name_plural = "Advertisements"

    def __str__(self):
        return self.title

class AdvertisementImage(models.Model):
    advertisement = models.ForeignKey(Advertisement, related_name='images', on_delete=models.CASCADE)
    image = models.ImageField(upload_to='advertisements/')

    def __str__(self):
        return f"Image for {self.advertisement.title}"

@receiver(pre_save, sender=Advertisement)
def generate_serial_number(sender, instance, **kwargs):
    if not instance.serial_number:
        while True:
            serial = ''.join(random.choices(string.ascii_uppercase + string.digits, k=5))
            if not Advertisement.objects.filter(serial_number=serial).exists():
                instance.serial_number = serial
                break