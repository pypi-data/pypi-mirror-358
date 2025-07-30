import django
import os
from unittest import mock
from django.urls import reverse, include, re_path
from django.conf import settings
from rest_framework.test import APITestCase


def setup_settings(settings):
    settings.XX = "1"
    settings.SECRET_KEY = "ss"
    settings.ROOT_URLCONF = __name__


os.environ["DJANGO_SETTINGS_MODULE"] = "tests.mock_settings"


setup_settings(settings)
django.setup()

urlpatterns = [
    re_path(r'^table/api/', include('sparrow_cloud.apps.table_api.urls')),
]


class TestTableAPI(APITestCase):

    def setUp(self):
        setup_settings(settings)
        django.setup()

    def test_table_api_no_parameter(self):
        """无参数"""
        url = reverse('table_api')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 400)
    
    def test_table_api_bad_parameter(self):
        """错误参数"""
        filter_data = {
            "app_lable_model": "table_api.model",
            "filter_condition": {"brand_num": "1", "name": "lisi"}
        }
        url = reverse('table_api')
        response = self.client.get(path=url, data=filter_data)
        self.assertEqual(response.status_code, 400)
