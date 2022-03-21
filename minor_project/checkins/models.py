from django.db import models
from django.db.models import Func

# Create your models here.
class Month (Func):
    function = 'STRFTIME'
    template = '%(function)s("%%m", %(expressions)s)'
    output_field = models.IntegerField()

class Invites(models.Model):
    name = models.CharField(max_length=64)
    email = models.EmailField()
    event = models.CharField(max_length=64, null=True)
    img = models.ImageField(upload_to='images/')

class Checkins(models.Model):
    name = models.CharField(max_length=64, null=True)
    email = models.EmailField(null=True)
    event = models.CharField(max_length=64, null=True)
    status = models.BooleanField(default=False)
    checkinType = models.CharField(max_length = 64, null=True)

class Event(models.Model):
    user = models.CharField(max_length = 64)
    title = models.CharField(max_length=64)
    date = models.DateField()
    budget = models.IntegerField()
    description = models.CharField(max_length=64)
    current = models.BooleanField(default=False, null= True)

    def __str__(self):
        return f"{self.id}  {self.title}   {self.date}   {self.budget}  {self.description}"