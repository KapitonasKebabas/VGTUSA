#from asyncio.windows_events import NULL
from django.db import models
from django.contrib.auth.models import User

# Create your models here.
class infoProject(models.Model):
    id = models.AutoField(primary_key=True, editable=False, null=False)
    pavadinimas = models.CharField(max_length=50)
    busena = models.IntegerField()
    data = models.DateField()
    aprasymas = models.TextField()
    author = models.IntegerField()
    author_name = models.TextField()
    moderators = models.TextField(default="")

class toDoList(models.Model):
    task = models.TextField()
    busena = models.IntegerField()
    project = models.ForeignKey(infoProject, on_delete=models.CASCADE)

class user_projects(models.Model):
    userId = models.IntegerField()
    projectsId = models.TextField()

class infoUAB(models.Model):
    id = models.AutoField(primary_key=True, editable=False, null=False)
    pavadinimas = models.CharField(max_length=100)
    busena = models.IntegerField()
    tipas = models.CharField(max_length=50)
    email = models.CharField(max_length=100)
    numeris = models.CharField(max_length=50)
    tekstas = models.TextField()

class UABinfoTracker(models.Model):
    id = models.AutoField(primary_key=True, editable=False, null=False)
    UABid = models.IntegerField()
    authId = models.IntegerField()
    authName = models.CharField(max_length=50)
    tekstas = models.TextField()
    date = models.DateField()
    busena = models.IntegerField(default=0)

class projectUABs(models.Model):
    id = models.AutoField(primary_key=True, editable=False, null=False)
    UABid = models.IntegerField()
    pavadinimasUAB = models.CharField(max_length=100)
    projectId = models.IntegerField()
    pavadinimasProject = models.CharField(max_length=100)
    tipas = models.CharField(max_length=50)
    susisiekta = models.BooleanField(default=False)
    email = models.CharField(max_length=100, default="")

class kodai(models.Model):
    id = models.AutoField(primary_key=True, editable=False, null=False)
    kodas = models.TextField(max_length=20)
    kiek = models.IntegerField()
