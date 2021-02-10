from django.urls import path
from . import views

app_name = 'cms'
urlpatterns = [
    path('article', views.ArticleView.as_view(), name='article'),
    path('category', views.CategoryView.as_view(), name='category'),
    path('login', views.LoginView.as_view(), name='login'),
]

