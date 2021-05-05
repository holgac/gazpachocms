from django.urls import reverse
import datetime
from ..models import Category
from .base import RestTestMixin, BaseTestCase, ObjectType

class ArticleTestCase(BaseTestCase, RestTestMixin):
  '''
  def __init__(self, *args: Any, **kwargs: Any):
    super(TestCase, self).__init__(*args, **kwargs)
  '''
  rest_path = reverse('cms:api:article')

  def _test_create_extra(self, constructed: ObjectType, persisted: ObjectType) -> None:
    self.assertEqual(persisted['author'], self.user.id)

  def _construct(self, index: int = 0) -> ObjectType:
    return {
      'name': f'{self._name()}-{index}',
      'title': 'some title',
      'content': 'Article content',
      'category': 0,
    }

  def _modify(self, data: ObjectType) -> None:
    for key in ['name', 'title', 'content']:
      data[key] = f'{data[key]}_modified'
    data['category'] = 1
