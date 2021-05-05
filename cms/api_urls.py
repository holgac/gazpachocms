from django.urls import path
from . import views

app_name = 'api'
urlpatterns = [
  path('article', views.ArticleView.as_view(), name='article'),
  path('category', views.CategoryView.as_view(), name='category'),
]
