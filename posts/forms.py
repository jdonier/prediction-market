#-*- coding: utf-8 -*-
from django import forms
 
class SignupForm(forms.Form):
    name = forms.CharField(label="User Name", max_length=30)
    email = forms.EmailField(label=u"Email")
    pwd = forms.CharField(label="Password", widget=forms.PasswordInput)
	
class ConnexionForm(forms.Form):
    username = forms.CharField(label="Nom d'utilisateur", max_length=30)
    password = forms.CharField(label="Mot de passe", widget=forms.PasswordInput)
	
	
class MarketForm(forms.Form):
    name = forms.CharField(label="Title", max_length=30)
    description = forms.CharField(label="Description",  max_length=255)