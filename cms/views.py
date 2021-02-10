from django.views import View
from django.contrib.auth.views import LoginView as BaseLoginView
from django.http import HttpRequest, HttpResponse, HttpResponseForbidden, HttpResponseNotFound, HttpResponseBadRequest
from django.middleware import csrf
from django.contrib.auth import authenticate
import json
from .services import ArticleService, ServiceError, AlreadyExistsError, CategoryService
from typing import List
from .models import Article
from django.contrib.auth.models import User
from django.http import QueryDict

class CmsViewMixin:
  def _handle_service_error(self, e: ServiceError) -> HttpResponse:
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
  template_name='test.html'

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
      return self._handle_service_error(e)
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
      return self._handle_service_error(e)
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
      return self._handle_service_error(e)
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
      return self._handle_service_error(e)
    return HttpResponse(json.dumps(category.serialize()))

  def delete(self, request: HttpRequest) -> HttpResponse:
    if not request.user.is_authenticated:
      return HttpResponseForbidden()
    return HttpResponse(json.dumps(request.GET))
