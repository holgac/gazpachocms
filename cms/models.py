from django.db import models
from typing import Dict, Union, Optional
from django.contrib.auth.models import User
import datetime
# Create your models here.

class SerializeSettings:
  def __init__(self) -> None:
    pass

def timenow() -> int:
  return int(datetime.datetime.now().timestamp() * 1000.0)

class DbObject(models.Model):
  id = models.AutoField(primary_key=True)
  ctime = models.BigIntegerField('Creation time (ms)', default=timenow)
  mtime = models.BigIntegerField('Modification time (ms)', default=timenow)
  class Meta:
    abstract = True
    indexes = [
        models.Index(fields=['ctime']),
    ]
  def _serialize_self(self, ss: SerializeSettings) -> Dict[str, Union[int, str, bool]]:
    return {
        'id': self.id,
        'ctime': self.ctime,
        'mtime': self.mtime,
        }
  def serialize(self, ss: Optional[SerializeSettings] = None) -> Dict[str, Union[int, str, bool]]:
    data = {}
    ss = ss or SerializeSettings()
    for cls in type(self).__mro__:
      if '_serialize_self' in dir(cls):
        data.update(cls._serialize_self(self, ss)) # type: ignore
    return data


class NamedDbObject(DbObject):
  name = models.CharField('Name of the object', max_length=128, unique=True)
  class Meta:
    abstract = True
    indexes = DbObject.Meta.indexes
  def __str__(self) -> str:
    return self.name
  def _serialize_self(self, ss: SerializeSettings) -> Dict[str, Union[int, str, bool]]:
    return {
        'name': self.name,
        }

class Category(NamedDbObject):
  long_name = models.CharField('Long name for display', max_length=128)
  parent = models.IntegerField('Parent category', default=0)
  class Meta:
    indexes = NamedDbObject.Meta.indexes + [
        models.Index(fields=['parent']),
    ]
  def _serialize_self(self, ss: SerializeSettings) -> Dict[str, Union[int, str, bool]]:
    return {
        'parent': self.parent,
        'long_name': self.long_name,
        }


class UserSettings(NamedDbObject):
  userid = models.IntegerField('Id of the user', unique=True)

class Article(NamedDbObject):
  author = models.IntegerField('Author of the article')
  category = models.IntegerField('Category of the article', default=0)
  title = models.CharField('Title of the article', max_length=128)
  content = models.TextField('Content of the article')
  def _serialize_self(self, ss: SerializeSettings) -> Dict[str, Union[int, str, bool]]:
    return {
        'author': self.author,
        'category': self.category,
        'title': self.title,
        'content': self.content,
        }
