from django.db import models

# Create your models here.
from django.db import models


class Province(models.Model):
    name = models.CharField(max_length=100, unique=True)

    class Meta:
        ordering = ['name']

    def __str__(self):
        return self.name


class District(models.Model):
    province = models.ForeignKey(
        Province,
        on_delete=models.CASCADE,
        related_name='districts'
    )
    name = models.CharField(max_length=100)

    class Meta:
        ordering = ['name']
        unique_together = ('province', 'name')

    def __str__(self):
        return f"{self.name}, {self.province.name}"