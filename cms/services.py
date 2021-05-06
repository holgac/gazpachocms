import datetime
import re
from typing import List, Optional

from django.db.models import QuerySet
from django.db.utils import DatabaseError, IntegrityError

from .models import Article, Category


class ServiceError(Exception):
  pass


class AlreadyExistsError(ServiceError):
  def __init__(self, key: str):
    self.key: str = key


class ServiceBase:
  @classmethod
  def _handle_database_error(cls, e: DatabaseError) -> None:
    if isinstance(e, IntegrityError):
      code, msg = e.args
      if code == 1062:
        match = re.match("Duplicate entry '([^']+)' for key '([^']+)'", msg)
        if match is None:
          raise Exception('Cannot parse ' + msg)
        raise AlreadyExistsError(match.group(2))
      raise e


class ArticleService(ServiceBase):
  @classmethod
  def _get_base_query(
      cls,
      range_query: bool = True,
      only_visible: bool = True,
  ) -> QuerySet[Article]:
    q = Article.objects.all()
    if range_query:
      q = q.filter(direct_links_only=False)
    if only_visible:
      q = q.filter(visible=True)
    return q

  @classmethod
  def get_by_id(cls, id: int) -> Optional[Article]:
    try:
      return cls._get_base_query(range_query=False).get(id=id, visible=True)
    except Article.DoesNotExist:
      return None

  @classmethod
  def get_by_name(cls, name: str) -> Optional[Article]:
    try:
      return cls._get_base_query(range_query=False).get(name=name)
    except Article.DoesNotExist:
      return None

  @classmethod
  def get_by_category(cls, category: Category, include_descendants: bool = True) -> List[Article]:
    categories = set([category.id])
    if include_descendants:
      prev_categories = set(categories)
      while prev_categories:
        result = set(cat.id for cat in Category.objects.filter(parent__in=prev_categories))
        prev_categories = result.difference(categories)
        categories.update(prev_categories)
    return list(cls._get_base_query().filter(category__in=categories))

  @classmethod
  def get_all(cls) -> List[Article]:
    # TODO: add some filters like start time, limit etc
    return list(cls._get_base_query())

  @classmethod
  def create(
      cls,
      name: str,
      author: int,
      title: str,
      content: str,
      category: int,
      visible: bool,
      direct_links_only: bool,
  ) -> Article:
    a = Article(
      name=name,
      author=author,
      title=title,
      content=content,
      category=category,
      visible=visible,
      direct_links_only=direct_links_only,
    )
    try:
      a.save()
    except DatabaseError as e:
      ServiceBase._handle_database_error(e)
    return a

  @classmethod
  def update(
      cls,
      article: Article,
      name: str,
      author: Optional[int],
      title: str,
      content: str,
      category: int,
      visible: bool,
      direct_links_only: bool,
  ) -> Article:
    article.name = name
    article.title = title
    article.content = content
    article.category = category
    article.visible = visible
    article.direct_links_only = direct_links_only
    if author is not None:
      article.author = author
    article.mtime = int(datetime.datetime.now().timestamp() * 1000.0)
    try:
      article.save()
    except DatabaseError as e:
      ServiceBase._handle_database_error(e)
    return article


class CategoryService(ServiceBase):

  @classmethod
  def get_by_id(cls, id: int) -> Optional[Category]:
    try:
      return Category.objects.get(id=id)
    except Category.DoesNotExist:
      return None

  @classmethod
  def get_by_name(cls, name: str) -> Optional[Category]:
    try:
      return Category.objects.get(name=name)
    except Category.DoesNotExist:
      return None

  @classmethod
  def get_all(cls) -> List[Category]:
    return [a for a in Category.objects.all()]

  @classmethod
  def create(
      cls,
      name: str,
      long_name: str,
      parent: int,
  ) -> Category:
    a = Category(
      name=name,
      long_name=long_name,
      parent=parent,
    )
    try:
      a.save()
    except DatabaseError as e:
      ServiceBase._handle_database_error(e)
    return a

  @classmethod
  def update(cls,
             category: Category,
             name: str,
             long_name: str,
             parent: int,
             ) -> Category:
    category.name = name
    category.long_name = long_name
    category.parent = parent
    category.mtime = int(datetime.datetime.now().timestamp() * 1000.0)
    try:
      category.save()
    except DatabaseError as e:
      ServiceBase._handle_database_error(e)
    return category
