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

  def _construct(self, index: int = 0, visible: bool = True, direct_links_only: bool = False) -> ObjectType:
    return {
      'name': f'{self._name()}-{index}',
      'title': 'some title',
      'content': 'Article content',
      'category': 0,
      'visible': visible,
      'direct_links_only': direct_links_only,
    }

  def _modify(self, data: ObjectType) -> None:
    for key in ['name', 'title', 'content']:
      data[key] = f'{data[key]}_modified'
    data['category'] = 1

  def test_visible(self) -> None:
    self.assertEqual(self._get_objects(self.rest_path), [])
    self._login()
    a1 = self._create_object(self.rest_path, self._construct(0))
    a2 = self._create_object(self.rest_path, self._construct(1, visible=False))
    objects = self._get_objects(self.rest_path)
    self.assertEqual(len(objects), 1)
    self.assertEqual(objects[0]['id'], a1['id'])
    readback = self._get_object(self.rest_path, a2['id'], 404)
    self.assertEqual(readback, {})

  def test_direct_links_only(self) -> None:
    self.assertEqual(self._get_objects(self.rest_path), [])
    self._login()
    a1 = self._create_object(self.rest_path, self._construct(0))
    a2 = self._create_object(self.rest_path, self._construct(1, direct_links_only=True))
    objects = self._get_objects(self.rest_path)
    self.assertEqual(len(objects), 1)
    self.assertEqual(objects[0]['id'], a1['id'])
    readback = self._get_object(self.rest_path, a2['id'])
    for key in a2:
      self.assertEqual(a2[key], readback[key])
