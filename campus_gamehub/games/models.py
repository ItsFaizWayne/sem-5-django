from django.db import models
from django.conf import settings

class Game(models.Model):
    title = models.CharField(max_length=100)
    description = models.TextField()
    image = models.ImageField(upload_to='games/', blank=True, null=True)
    available = models.BooleanField(default=True)

    # NEW FIELD
    added_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="games_added",
        null=True,
        blank=True
    )

    def __str__(self):
        return self.title
