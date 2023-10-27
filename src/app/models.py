from django.db import models

# Create your models here.


class Producer(models.Model):

    name = models.TextField()


class Studios(models.Model):
    name = models.TextField()


class Movie(models.Model):
    name = models.TextField()
    producer = models.ForeignKey(to=Producer, on_delete=models.CASCADE)
    studios = models.ForeignKey(to=Studios, on_delete=models.CASCADE)


class Prize(models.Model):
    year = models.IntegerField()
    movie = models.ForeignKey(to=Movie, on_delete=models.CASCADE)
    winner = models.BooleanField()
