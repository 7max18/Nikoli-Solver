from django.shortcuts import render
from django.http import HttpResponseRedirect
from django.views import generic
from django.views.generic.edit import FormView
from . import forms
# Create your views here.

class HashiFormView(FormView) :
    template_name = 'hashi/index.html'

    def form_valid(self, form):

