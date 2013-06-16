from django.db import models
from django.contrib.auth.models import User
from django.db.models import Sum
from django.db.models import Q
	   
class TradeManager(models.Manager):		   
	def limits(self, id_user, id_market):
		user=User.objects.get(id=id_user)
		trader=Trader.objects.get(user=user)
		market=Market.objects.get(id=id_market)
		limits=[]
		limits.append(Trade.objects.filter(trader=trader, market=market, type=0).aggregate(Sum('volume'))['volume__sum'])
		limits.append(Trade.objects.filter(trader=trader, market=market, type=1).aggregate(Sum('volume'))['volume__sum'])
		if limits[0]==None:
			limits[0]=0
		if limits[1]==None:
			limits[1]=0
		return limits
	def alllimits(self, id_market):
		market=Market.objects.get(id=id_market)
		limits=[]
		limits.append(Trade.objects.filter(market=market, type=0).aggregate(Sum('volume'))['volume__sum'])
		limits.append(Trade.objects.filter(market=market, type=1).aggregate(Sum('volume'))['volume__sum'])
		if limits[0]==None:
			limits[0]=0
		if limits[1]==None:
			limits[1]=0
		return limits	

class TraderManager(models.Manager):
	def balance(self, id_user):
		user=User.objects.get(id=id_user)
		trader=Trader.objects.get(user=user)
		balance=trader.balance
		limitSell=Trade.objects.filter(trader=trader, type=0).aggregate(Sum('volume'))['volume__sum']
		if limitSell==None:
			limitSell=0
		limitBuy=Trade.objects.filter(trader=trader, type=1).aggregate(Sum('volume'))['volume__sum']
		if limitBuy==None:
			limitBuy=0
		matchedSell=Matched.objects.filter(Q(trader=trader) & Q(type=0) | Q(type=2) ).aggregate(Sum('volume'))['volume__sum']
		if matchedSell==None:
			matchedSell=0
		matchedBuy=Matched.objects.filter(Q(trader=trader) & Q(type=1) | Q(type=3) ).aggregate(Sum('volume'))['volume__sum']
		if matchedBuy==None:
			matchedBuy=0		
		balance=balance-max(abs(limitBuy+matchedBuy-matchedSell), abs(limitSell+matchedSell-matchedBuy))
		return balance
		
class Trader(models.Model):
	user = models.OneToOneField(User)  # La liaison OneToOne vers le modèle User
	balance = models.DecimalField(max_digits=16, decimal_places=9, default=0)
	objects=TraderManager()
	
	def __unicode__(self):
		return u"Profil de {0}".format(self.user.username)
		
class Market(models.Model):
	name = models.CharField(max_length=255)
	creator = models.CharField(max_length=255)
	description = models.CharField(max_length=255)
	votes = models.ManyToManyField(Trader, through='Trade')
	
	def __unicode__(self):
           return self.name
		   
class Trade(models.Model):
	trader = models.ForeignKey(Trader)
	market = models.ForeignKey(Market)
	date = models.DateTimeField(auto_now_add=True)
	type = models.IntegerField()
	volume=models.DecimalField(max_digits=16, decimal_places=9)
	price=models.DecimalField(max_digits=4, decimal_places=2)
	matcher = models.IntegerField(default=0)
	objects=TradeManager()
	
	def __unicode__(self):
           return self.id	
		   
class Matched(models.Model):
	trader = models.ForeignKey(Trader)
	market = models.ForeignKey(Market)
	date = models.DateTimeField(auto_now_add=True)
	type = models.IntegerField()
	volume=models.DecimalField(max_digits=16, decimal_places=9)
	price=models.DecimalField(max_digits=4, decimal_places=2)
	matcher = models.IntegerField(default=0)
	objects=TradeManager()
	
	def __unicode__(self):
           return self.id		