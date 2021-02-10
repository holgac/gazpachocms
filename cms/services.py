from .models import Article, Category
from typing import List, Optional, TypeVar, Generic
import datetime
from django.db.utils import DatabaseError, IntegrityError
import re

class ServiceError(Exception):
  pass

class AlreadyExistsError(ServiceError):
  def __init__(self, key: str):
    self.key: str = key

class ServiceBase:
  @staticmethod
  def _handle_database_error(e: DatabaseError) -> None:
    if isinstance(e, IntegrityError):
      code, msg = e.args
      if code == 1062:
        match = re.match("Duplicate entry '([^']+)' for key '([^']+)'", msg)
        if match is None:
          raise Exception('Cannot parse ' + msg)
        raise AlreadyExistsError(match.group(2))
      raise e

class ArticleService(ServiceBase):
  @staticmethod
  def get_by_id(id: int) -> Optional[Article]:
    try:
      return Article.objects.get(id=id)
    except Article.DoesNotExist:
      return None

  @staticmethod
  def get_by_name(name: str) -> Article:
    return Article.objects.get(name=name)

  @staticmethod
  def get_by_category(category: str, include_descendants: bool) -> List[Article]:
    return []

  @staticmethod
  def get_all() -> List[Article]:
    return [a for a in Article.objects.all()]

  @staticmethod
  def create(
      name: str,
      author: int,
      title: str,
      content: str,
      category: int,
  ) -> Article:
    a = Article(
        name=name,
        author=author,
        title=title,
        content=content,
        category=category,
      )
    try:
      a.save()
    except DatabaseError as e:
      ServiceBase._handle_database_error(e)
    return a

  @staticmethod
  def update(
      article: Article,
      name: str,
      author: Optional[int],
      title: str,
      content: str,
      category: int,
  ) -> Article:
    article.name = name
    article.title = title
    article.content = content
    article.category = category
    if author is not None:
      article.author = author
    article.mtime = int(datetime.datetime.now().timestamp() * 1000.0)
    try:
      article.save()
    except DatabaseError as e:
      ServiceBase._handle_database_error(e)
    return article

class CategoryService(ServiceBase):
  @staticmethod
  def get_by_id(id: int) -> Optional[Category]:
    try:
      return Category.objects.get(id=id)
    except Category.DoesNotExist:
      return None

  @staticmethod
  def get_by_name(name: str) -> Category:
    return Category.objects.get(name=name)

  @staticmethod
  def get_all() -> List[Category]:
    return [a for a in Category.objects.all()]

  @staticmethod
  def create(
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

  @staticmethod
  def update(
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
