from django.shortcuts import render
from django.http import HttpResponse, HttpRequest

# Create your views here.

def index(request: HttpRequest) -> HttpResponse:
  return HttpResponse('test' + str(request.__class__))
