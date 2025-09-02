
# Create your models here.
from django.db import models

class WasteImage(models.Model):
    image = models.ImageField(upload_to='uploads/')
    uploaded_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"WasteImage {self.id}"
