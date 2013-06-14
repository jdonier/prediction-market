from django.db import models
from django.contrib.auth.models import User
 
class Voter(models.Model):
    user = models.OneToOneField(User)  # La liaison OneToOne vers le modèle User
    points = models.IntegerField(default=10)
	
    def __unicode__(self):
        return u"Profil de {0}".format(self.user.username)
		
class Market(models.Model):
	name = models.CharField(max_length=255)
	creator = models.CharField(max_length=255)
	description = models.CharField(max_length=255)
	nbYes = models.IntegerField(default=0)
	nbNo = models.IntegerField(default=0)
	votes = models.ManyToManyField(Voter, through='Vote')
	
	def __unicode__(self):
           return self.name
		   
class Vote(models.Model):
	voter = models.ForeignKey(Voter)
	market = models.ForeignKey(Market)
	vote = models.BooleanField()
	
	def __unicode__(self):
           return self.id	