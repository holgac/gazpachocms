import datetime
import inspect
import json
from typing import Dict, List, Union, cast

from django.contrib.auth.models import User
from django.test import TestCase, Client
from django.urls import reverse

ObjectType = Dict[str, Union[str, int, bool]]


# TODO: static functions
class BaseTestCase(TestCase):
  def setUp(self) -> None:
    super().setUp()
    self.client = Client()
    self.creds = {
      'username': 'test',
      'password': 'pwd',
    }
    self.user = User.objects.create_user(**self.creds)
    self.maxDiff = None

  def _name(self, suffix: str = '') -> str:
    for frame in inspect.stack():
      if frame.frame.f_code.co_name.startswith('test_'):
        return frame.frame.f_code.co_name + suffix
    raise Exception()

  def _login(self) -> None:
    resp = self.client.post(reverse('cms:login'), self.creds)
    self.assertEqual(resp.status_code, 302)

  def _deserialize(self, raw_data: str) -> ObjectType:
    data = json.loads(raw_data)
    return {key: value for key, value in data.items()}

  def _get_object(self, path: str, obj_id: int, expected_code: int = 200) -> ObjectType:
    resp = self.client.get(f'{path}?id={obj_id}')
    self.assertEqual(resp.status_code, expected_code)
    if 400 <= expected_code < 500:
      return {}
    return self._deserialize(resp.content.decode('UTF-8'))

  def _get_objects(self, path: str, expected_code: int = 200) -> List[ObjectType]:
    resp = self.client.get(path)
    self.assertEqual(resp.status_code, expected_code)
    if 400 <= expected_code < 500:
      return []
    content = json.loads(resp.content.decode('UTF-8'))
    return [c for c in content]

  def _create_object(
      self,
      path: str,
      data: ObjectType,
      expected_code: int = 200,
  ) -> ObjectType:
    resp = self.client.post(path, data, content_type='application/json')
    self.assertEqual(resp.status_code, expected_code)
    if 400 <= expected_code < 500:
      return {}
    return self._deserialize(resp.content.decode('UTF-8'))

  def _update_object(
      self,
      path: str,
      data: ObjectType,
      expected_code: int = 200,
  ) -> ObjectType:
    resp = self.client.put(
      path,
      data,
      'application/json')
    self.assertEqual(resp.status_code, expected_code)
    if 400 <= expected_code < 500:
      return {}
    return self._deserialize(resp.content.decode('UTF-8'))


class RestTestMixin:
  rest_path = ''

  def _test_create_extra(self, constructed: ObjectType, persisted: ObjectType) -> None:
    pass

  def _modify(self, data: ObjectType) -> None:
    pass

  def _construct(self, index: int = 0) -> ObjectType:
    pass

  def test_create_not_logged_in(self) -> None:
    test = cast(BaseTestCase, self)
    test._create_object(self.rest_path, self._construct(), expected_code=403)

  def test_create_single(self) -> None:
    test = cast(BaseTestCase, self)
    test._login()
    constructed = self._construct()
    time_before = int(datetime.datetime.now().timestamp() * 1000.0)
    persisted = test._create_object(self.rest_path, constructed)
    time_after = int(datetime.datetime.now().timestamp() * 1000.0)
    for key in constructed:
      test.assertEqual(persisted[key], constructed[key], f'{key} differs')
    test.assertGreater(persisted['ctime'], time_before)
    test.assertLess(persisted['ctime'], time_after)
    test.assertGreater(persisted['mtime'], time_before)
    test.assertLess(persisted['mtime'], time_after)
    self._test_create_extra(constructed, persisted)

  def test_create_duplicate(self) -> None:
    test = cast(BaseTestCase, self)
    test._login()
    obj = self._construct()
    persisted = test._create_object(self.rest_path, obj)
    test._create_object(self.rest_path, obj, 400)

  def test_get(self) -> None:
    test = cast(BaseTestCase, self)
    test._login()
    obj = test._create_object(self.rest_path, self._construct())
    readback = test._get_object(self.rest_path, obj['id'])
    for key in obj:
      test.assertEqual(readback[key], obj[key])

  def test_get_all(self) -> None:
    test = cast(BaseTestCase, self)
    test.assertEqual(test._get_objects(self.rest_path), [])
    test._login()
    objects = [
      test._create_object(self.rest_path, self._construct(i))
      for i in range(10)
    ]
    test.assertEqual(test._get_objects(self.rest_path), objects)

  def test_update(self) -> None:
    test = cast(BaseTestCase, self)
    test._login()
    obj_before = test._create_object(self.rest_path, self._construct())
    self._modify(obj_before)
    time_before = int(datetime.datetime.now().timestamp() * 1000.0)
    obj_after = test._update_object(self.rest_path, obj_before)
    time_after = int(datetime.datetime.now().timestamp() * 1000.0)

    for key in obj_before:
      if key == 'mtime':
        test.assertGreater(obj_after[key], obj_before[key])
      else:
        test.assertEqual(obj_after[key], obj_before[key])
    test.assertGreater(obj_after['mtime'], time_before)
    test.assertLess(obj_after['mtime'], time_after)

  def test_update_non_existing(self) -> None:
    test = cast(BaseTestCase, self)
    obj = self._construct()
    obj['id'] = -1
    test._update_object(self.rest_path, obj, 403)
    test._login()
    test._update_object(self.rest_path, obj, 404)

  def test_update_duplicate(self) -> None:
    test = cast(BaseTestCase, self)
    test._login()
    obj1 = test._create_object(self.rest_path, self._construct(1))
    obj2 = test._create_object(self.rest_path, self._construct(2))
    obj1['id'] = obj2['id']
    test._update_object(self.rest_path, obj1, 400)
