from django.urls import reverse
import datetime
from ..models import Category
from .base import RestTestMixin, BaseTestCase, ObjectType

class CategoryTestCase(BaseTestCase, RestTestMixin):
  rest_path = reverse('cms:api:category')

  def _construct(self, index: int = 0) -> ObjectType:
    return {
      'name': f'{self._name()}-{index}',
      'long_name': 'Long name',
      'parent': 0,
    }

  def _modify(self, data: ObjectType) -> None:
    for key in ['name', 'long_name']:
      data[key] = f'{data[key]}_modified'
