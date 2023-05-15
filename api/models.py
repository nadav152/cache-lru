from django.db import models
import logging


class Book(models.Model):
    name = models.CharField(max_length=128, db_index=True, unique=True)
    author = models.CharField(max_length=128, db_index=True, unique=True)
    pages_amount = models.PositiveIntegerField()