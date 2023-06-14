from django.db import models


# Create your models here.


class Family(models.Model):
    name = models.CharField(max_length=100)

    class Meta:
        verbose_name_plural = "Families"

    def __str__(self):
        return f"{self.name} Family"
