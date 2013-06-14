#-*- coding: utf-8 -*-
from django.http import HttpResponse, HttpResponseRedirect, Http404
from django.shortcuts import redirect
from datetime import datetime
from django.shortcuts import render, get_object_or_404
import string, random
from django.core.urlresolvers import reverse
from posts.forms import SignupForm, ConnexionForm, MarketForm
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login, logout 
from django.core.paginator import Paginator, EmptyPage  # Ne pas oublier l'importation
from django.contrib.auth.decorators import login_required
from posts.models import Market, Voter, Vote
from django.contrib.auth.decorators import permission_required
from django.contrib.admin.views.decorators import staff_member_required


def sign_up(request):
    if request.method == 'POST':  # S'il s'agit d'une requête POST
        form = SignupForm(request.POST)  # Nous reprenons les données
 
        if form.is_valid():
			user=User()
			user.username = form.cleaned_data['name']
			user.email = form.cleaned_data['email']
			user.set_password(form.cleaned_data['pwd'])
			user.save()
			voter=Voter(user=user)
			voter.save()
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
	voter=Voter.objects.get(user=user)
	markets=Market.objects.all()
	votes=Vote.objects.all()
	myvotes=[]
	for market in markets:
		myvotes.append({ 'market':market.name, 'votesyes':votes.filter(market=market, voter=voter, vote=True).count(), 'votesno':votes.filter(market=market, vote=False).count()})
	titre=u'{0}'.format(user.username)
	return render(request, 'posts/show_user.html', locals())
	
def all_users(request, page=1):	
	titre="All Users"
	voters=Voter.objects.all()
	paginator = Paginator(voters, 4)
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
	
@login_required	
def vote(request, id_market, yesno):	
	market=Market.objects.get(id=id_market)
	titre=u'{0}'.format(market.name)
	if request.user.is_authenticated:
		voter=Voter.objects.get(user=request.user)
		vote=Vote()
		if voter.points>0:
			voter.points-=1
			vote.market=market
			vote.voter=voter
			if yesno=='1':
				market.nbYes+=1
				vote.vote=True
			else:
				market.nbNo+=1
				vote.vote=False
			market.save()
			voter.save()
			vote.save()
	return render(request, 'posts/show_market.html', locals())	
	
@staff_member_required	
def settle(request, id_market, yesno):	
	market=Market.objects.get(id=id_market)
	titre=""
	votes=Vote.objects.filter(market=market)
	for vote in votes:
		if (vote.vote==True and yesno=='1') or (vote.vote==False and yesno=='0'):			
			voter=vote.voter
			voter.points+=2
			voter.save()
	market.delete()
	return redirect(reverse(all_markets))		
	
@login_required	
def market(request, id_market):	
	market=Market.objects.get(id=id_market)
	titre=u'{0}'.format(market.name)
	voter=Voter()
	if request.user.is_authenticated:
		voter=Voter.objects.get(user=request.user)
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
	if request.user.is_authenticated:
		return redirect(reverse(user, kwargs={'id_user':request.user.id}))
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
 