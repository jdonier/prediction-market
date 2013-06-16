#-*- coding: utf-8 -*-
from django.http import HttpResponse, HttpResponseRedirect, Http404
from django.shortcuts import redirect
from datetime import datetime
from django.shortcuts import render, get_object_or_404
import string, random
from django.core.urlresolvers import reverse
from posts.forms import SignupForm, ConnexionForm, MarketForm, TradeForm
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login, logout 
from django.core.paginator import Paginator, EmptyPage  # Ne pas oublier l'importation
from django.contrib.auth.decorators import login_required
from posts.models import Market, Trader, Trade, Matched
from django.contrib.auth.decorators import permission_required
from django.contrib.admin.views.decorators import staff_member_required
from django.db.models import Avg, Max, Min

def sign_up(request):
    if request.method == 'POST':  # S'il s'agit d'une requête POST
        form = SignupForm(request.POST)  # Nous reprenons les données
 
        if form.is_valid():
			user=User()
			user.username = form.cleaned_data['name']
			user.email = form.cleaned_data['email']
			user.set_password(form.cleaned_data['pwd'])
			user.save()
			trader=Trader(user=user)
			trader.balance=10
			trader.save()
			user = authenticate(username=form.cleaned_data['name'], password=form.cleaned_data['pwd'])  #Nous vérifions si les données sont correctes
			login(request, user)
			return redirect('posts.views.user', id_user=user.id)
    else: # Si ce n'est pas du POST, c'est probablement une requête GET
        form = SignupForm()  # Nous créons un formulaire vide
 
    return render(request, 'posts/sign_up.html', locals())

def sign_out(request):                                                                               
    logout(request)                                                                                     
    return redirect(reverse(sign_in))
	
def sign_in(request):
    error = False
 
    if request.method == "POST":
        form = ConnexionForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data["username"]  # Nous récupérons le nom d'utilisateur
            password = form.cleaned_data["password"]  # … et le mot de passe
            user = authenticate(username=username, password=password)  #Nous vérifions si les données sont correctes
            if user:  # Si l'objet renvoyé n'est pas None
				login(request, user)  # nous connectons l'utilisateur
				titre="{0}".format(username)
            else: #sinon une erreur sera affichée
                error = True
    else:
		form = ConnexionForm()
		titre="Sign In"
 
    return render(request, 'posts/sign_in.html',locals())

@login_required	
def user(request, id_user):	
	user=User.objects.get(id=id_user)
	trader=Trader.objects.get(user=user)
	markets=Market.objects.all()
	trades=Trade.objects.all()
	myTrades=[]
	for market in markets:
		myTrades.append({ 'market':market.name, 'Tradesyes':Trade.objects.limits(id_user=id_user, id_market=market.id)[1], 'Tradesno':Trade.objects.limits(id_user=id_user, id_market=market.id)[0]})
	titre=u'{0}'.format(user.username)
	return render(request, 'posts/show_user.html', locals())
	
def all_users(request, page=1):	
	titre="All Users"
	traders=Trader.objects.all()
	paginator = Paginator(traders, 4)
	try:
		minis = paginator.page(page)
	except EmptyPage:
		minis = paginator.page(paginator.num_pages)
	return render(request, 'posts/all_users.html', locals())	

@login_required	
def new_market(request):
    if request.method == 'POST':  # S'il s'agit d'une requête POST
        form = MarketForm(request.POST)  # Nous reprenons les données
 
        if form.is_valid():
			market=Market()
			market.name = form.cleaned_data['name']
			market.creator=request.user.username
			market.description = form.cleaned_data['description']
			market.save()
			return redirect('posts.views.market', id_market=market.id)
    else: # Si ce n'est pas du POST, c'est probablement une requête GET
        form = MarketForm()  # Nous créons un formulaire vide
 
    return render(request, 'posts/new_market.html', locals())
	
	
@staff_member_required	
def settle(request, id_market, yesno):	
	market=Market.objects.get(id=id_market)
	titre=""
	trades=Trade.objects.filter(market=market)
	limits=Trade.objects.alllimits(id_market=market.id)
	for trade in trades:
		if trade.type==1 and yesno=='1':
			trader=trade.trader
			trader.balance+=trade.volume/limits[1]*limits[0]
			trader.save()
		if trade.type==0 and yesno=='0':		
			trader=trade.trader
			trader.balance+=trade.volume/limits[0]*limits[1]
			trader.save()	
		if 	trade.type==1 and yesno=='0' or trade.type==0 and yesno=='1':
			trader.balance-=trade.volume
	market.delete()
	return redirect(reverse(all_markets))		
	
@login_required	
def market(request, id_market):	
	from django.db import connection
	market=Market.objects.get(id=id_market)
	titre=u'{0}'.format(market.name)
	trader=Trader()
	if request.user.is_authenticated:
		trader=Trader.objects.get(user=request.user)
		if request.method == 'POST':
			form = TradeForm(request.POST)
			if form.is_valid():
				volume=form.cleaned_data['volume']
				price=form.cleaned_data['price']
				type=form.cleaned_data['type']
				if volume<=Trader.objects.balance(id_user=request.user.id):
					execute(market, trader, type, price, volume)
		else:
			form = TradeForm()
		available=Trader.objects.balance(id_user=request.user.id)		
	limits=Trade.objects.alllimits(id_market=market.id)
	buyVol=limits[1]
	buySell=limits[0]
	cursor = connection.cursor()	
	cursor.execute("SELECT price price, sum(volume) volume FROM posts_trade WHERE type=1 GROUP BY price ORDER BY price DESC")
	buyOrders = dictfetchall(cursor)
	cursor = connection.cursor()	
	cursor.execute("SELECT price price, sum(volume) volume FROM posts_trade WHERE type=0 GROUP BY price ORDER BY price DESC")
	sellOrders = dictfetchall(cursor)
	return render(request, 'posts/show_market.html', locals())	

@staff_member_required	
def delete_market(request, id_market):	
	market=Market.objects.get(id=id_market)
	market.delete()
	titre="All Markets"
	return redirect(reverse(all_markets))	
	
	
def all_markets(request, page=1):	
	titre="Markets"
	markets=Market.objects.all()
	paginator = Paginator(markets, 4)
	try:
		minis = paginator.page(page)
	except EmptyPage:
		minis = paginator.page(paginator.num_pages)
	return render(request, 'posts/all_markets.html', locals())

	
@staff_member_required
def delete_user(request, id_user):	
	user=User.objects.get(id=id_user)
	user.delete()
	titre="All Users"
	return redirect(reverse(all_users))
	
def home(request):	
	titre="Home"
	return render(request, 'posts/home.html', locals())
	
def contact(request):
	titre="Contact"
	return render(request, 'posts/contact.html', locals())	
	
	
def help(request):
	titre="Help"
	return render(request, 'posts/help.html', locals())	
	
def about(request):
	titre="About"
	return render(request, 'posts/about.html', locals())	

def dictfetchall(cursor):
    "Returns all rows from a cursor as a dict"
    desc = cursor.description
    return [
        dict(zip([col[0] for col in desc], row))
        for row in cursor.fetchall()
    ]	
	
def execute(market, trader, type, price, volume):
	volToExec=volume
	while type=='1' and volToExec>0	and Trade.objects.filter(market=market, type=0).aggregate(Min('price'))["price__min"]<>None and Trade.objects.filter(market=market, type=0).aggregate(Min('price'))["price__min"]<=price:
		priceMin=Trade.objects.filter(market=market, type=0).aggregate(Min('price'))["price__min"]
		dateMin=Trade.objects.filter(market=market, price=priceMin, type=0).aggregate(Min('date'))["date__min"]
		order=Trade.objects.get(market=market, price=priceMin, date=dateMin, type=0)
		if order.volume<=volToExec:
			matched=Matched(trader=trader, market=market, type=1, price=order.price, volume=order.volume, matcher=order.trader.user.id) 
			matched2=Matched(trader=order.trader, market=market, type=2, price=order.price, volume=order.volume, matcher=trader.user.id) 
			volInt=order.volume
			order.delete()>0
			volToExec-=volInt
			matched.save()
			matched2.save()
		else:
			matched=Matched(trader=trader, market=market, type=1, price=order.price, volume=volToExec, matcher=order.trader.user.id) 
			matched2=Matched(trader=order.trader, market=market, type=2, price=order.price, volume=volToExec, matcher=trader.user.id) 
			order.volume-=volToExec	
			order.save()		
			volToExec=0
			matched.save()
			matched2.save()
			
	while type=='0' and volToExec>0 and Trade.objects.filter(market=market, type=1).aggregate(Max('price'))["price__max"]<>None and Trade.objects.filter(market=market, type=1).aggregate(Max('price'))["price__max"]>=price:
		priceMax=Trade.objects.filter(market=market, type=1).aggregate(Max('price'))["price__max"]
		dateMin=Trade.objects.filter(market=market, price=priceMax, type=1).aggregate(Min('date'))["date__min"]
		order=Trade.objects.get(market=market, price=priceMax, date=dateMin, type=1)	
		if order.volume<=volToExec:
			matched=Matched(trader=trader, market=market, type=0, price=order.price, volume=order.volume, matcher=order.trader.user.id) 
			matched2=Matched(trader=order.trader, market=market, type=3, price=order.price, volume=order.volume, matcher=trader.user.id) 
			volInt=order.volume
			order.delete()
			volToExec-=volInt
			matched.save()
			matched2.save()
		else:
			matched=Matched(trader=trader, market=market, type=0, price=order.price, volume=volToExec, matcher=order.trader.user.id) 
			matched2=Matched(trader=order.trader, market=market, type=3, price=order.price, volume=volToExec, matcher=trader.user.id) 
			order.volume-=volToExec	
			order.save()		
			volToExec=0
			matched.save()
			matched2.save()
			
	#Crée un limit order sur ce qui reste	
	if volToExec>0:
		trade=Trade(market=market, trader=trader, type=type, price=price, volume=volToExec)
		trade.save()