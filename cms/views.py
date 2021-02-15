from django.views import View
from django.contrib.auth.views import LoginView as BaseLoginView
from django.http import HttpRequest, HttpResponse, HttpResponseForbidden, HttpResponseNotFound, HttpResponseBadRequest
from django.middleware import csrf
from django.contrib.auth import authenticate
import json
from .services import ArticleService, ServiceError, AlreadyExistsError, CategoryService
from typing import Any, Dict, List
from .models import Article, Category
from django.contrib.auth.models import User
from django.http import QueryDict
from django.template.loader import render_to_string

class CmsViewMixin:
  def _gen_sidebar(self, name: str, url: str) -> Dict[Any, Any]:
    return {'name': name, 'url': url}
  def _get_sidebar_context(self) -> List[Dict[Any, Any]]:
    return [
        self._gen_sidebar('Home', '/'),
        self._gen_sidebar('About Me', '/a/about'),
        self._gen_sidebar('Articles about cats', '/c/cats'),
    ]
  def get_template_context(self, extra: Dict[Any, Any] = {}) -> Dict[Any, Any]:
    ctx = {
        'sidebar': [
          self._gen_sidebar('Home', '/'),
          self._gen_sidebar('About Me', '/a/about'),
          self._gen_sidebar('Articles about cats', '/c/cats'),
        ],
        'settings': {
          'title': 'GazpachoCMS',
          'slogan': 'JS-Free Content Management System',
        }
    }
    ctx.update(extra)
    print(json.dumps(ctx))
    return ctx

  def handle_service_error(self, e: ServiceError) -> HttpResponse:
    if isinstance(e, AlreadyExistsError):
      return HttpResponseBadRequest()
    # TODO: log and raise an unknown error
    raise e

class UserView(CmsViewMixin, View):
  def get(self, request: HttpRequest) -> HttpResponse:
    return HttpResponse(csrf.get_token(request))
  def head(self, request: HttpRequest) -> HttpResponse:
    return HttpResponse('head ' + str(request.__class__))
  def post(self, request: HttpRequest) -> HttpResponse:
    return HttpResponse('post ' + str(request.__class__))
  def put(self, request: HttpRequest) -> HttpResponse:
    return HttpResponse('put ' + str(request.__class__))

class LoginView(CmsViewMixin, BaseLoginView):
  template_name='index.pug'

class IndexView(CmsViewMixin, View):
  def _gen_article(self, title: str, url: str, content: str) -> Dict[str, str]:
    return {
        'title': title,
        'url': url,
        'content': content,
    }
  def get(self, request: HttpRequest) -> HttpResponse:
    return HttpResponse(render_to_string(
      'articles.html',
      self.get_template_context({'articles':[
        self._gen_article(f'article {i}', '/', 'article content')
        for i in range(10)
        ]}),
    ))

class ArticleView(CmsViewMixin, View):
  service = ArticleService

  def get(self, request: HttpRequest) -> HttpResponse:
    if 'id' in request.GET or 'name' in request.GET:
      if 'id' in request.GET:
        article = self.service.get_by_id(int(request.GET['id']))
      elif 'name' in request.GET:
        article = self.service.get_by_name(request.GET['name'])
      if article is None:
        return HttpResponseNotFound()
      return HttpResponse(json.dumps(article.serialize()))
    articles: List[Article] = []
    if 'category' in request.GET:
      articles = self.service.get_by_category(request.GET['category'],
          'descendants' in request.GET)
    else:
      articles = self.service.get_all()
    return HttpResponse(json.dumps([a.serialize() for a in articles]))

  def post(self, request: HttpRequest) -> HttpResponse:
    if not request.user.is_authenticated:
      return HttpResponseForbidden()
    try:
      article = self.service.create(
          name = request.POST['name'],
          author = request.user.id,
          title = request.POST['title'],
          content = request.POST['content'],
          category = int(request.POST['category']),
      )
    except ServiceError as e:
      return self.handle_service_error(e)
    return HttpResponse(json.dumps(article.serialize()))

  def put(self, request: HttpRequest) -> HttpResponse:
    if not request.user.is_authenticated:
      return HttpResponseForbidden()
    body = json.loads(request.body)
    article = self.service.get_by_id(int(body['id']))
    if article is None:
      return HttpResponseNotFound()
    try:
      article = self.service.update(
          article,
          name = body['name'],
          author = request.user.id if 'update_author' in body else article.author,
          title = body['title'],
          content = body['content'],
          category = int(body['category']),
      )

    except ServiceError as e:
      return self.handle_service_error(e)
    return HttpResponse(json.dumps(article.serialize()))

  def delete(self, request: HttpRequest) -> HttpResponse:
    if not request.user.is_authenticated:
      return HttpResponseForbidden()
    return HttpResponse(json.dumps(request.GET))

class CategoryView(CmsViewMixin, View):
  service = CategoryService

  def get(self, request: HttpRequest) -> HttpResponse:
    if 'id' in request.GET or 'name' in request.GET:
      if 'id' in request.GET:
        category = self.service.get_by_id(int(request.GET['id']))
      elif 'name' in request.GET:
        category = self.service.get_by_name(request.GET['name'])
      if category is None:
        return HttpResponseNotFound()
      return HttpResponse(json.dumps(category.serialize()))
    else:
      categories = self.service.get_all()
    return HttpResponse(json.dumps([a.serialize() for a in categories]))

  def post(self, request: HttpRequest) -> HttpResponse:
    if not request.user.is_authenticated:
      return HttpResponseForbidden()
    try:
      category = self.service.create(
          name = request.POST['name'],
          long_name = request.POST['long_name'],
          parent = int(request.POST['parent']),
      )
    except ServiceError as e:
      return self.handle_service_error(e)
    return HttpResponse(json.dumps(category.serialize()))

  def put(self, request: HttpRequest) -> HttpResponse:
    if not request.user.is_authenticated:
      return HttpResponseForbidden()
    body = json.loads(request.body)
    category = self.service.get_by_id(int(body['id']))
    if category is None:
      return HttpResponseNotFound()
    try:
      category = self.service.update(
          category,
          name = body['name'],
          long_name = body['long_name'],
          parent = int(body['parent']),
      )
    except ServiceError as e:
      return self.handle_service_error(e)
    return HttpResponse(json.dumps(category.serialize()))

  def delete(self, request: HttpRequest) -> HttpResponse:
    if not request.user.is_authenticated:
      return HttpResponseForbidden()
    return HttpResponse(json.dumps(request.GET))

def debug(request: HttpRequest) -> HttpResponse:
    if 'reset' in request.GET:
      # TODO: use service stuff or not?
      Article.objects.all().delete()
      Category.objects.all().delete()
      try:
        u = User.objects.get(username='test')
        u.delete()
      except User.DoesNotExist:
        pass
      u = User.objects.create_user(username='test', password='qwerasdf')
      food_category = CategoryService.create('food', 'Food', 0)
      animals_category = CategoryService.create('animals', 'Animals', 0)
      cats_category = CategoryService.create('cats', 'Cats', animals_category.id)
      big_cats_category = CategoryService.create('big_cats', 'Big Cats', cats_category.id)
      for cat in [food_category, animals_category, cats_category, big_cats_category]:
        for i in range(3):
          ArticleService.create(
              name = f'article_{cat.name}_{i}',
              author = u.id,
              title = f'article {i} title about {cat.long_name}',
              content= '\n'.join([f'{i}: {cat.name}{j}' for j in range(10)]),
              category = cat.id,
          )
      ArticleService.create(
          name = f'about',
          author = u.id,
          title = f'About page',
          content= 'This is about me',
          category = 0,
      )
    return HttpResponse('ok')
