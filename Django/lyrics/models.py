from django.db import models

# Create your models here.
class Group(models.Model):
    name = models.CharField(max_length=100)
    url = models.CharField(max_length=200)

    def __str__(self):
            return self.name