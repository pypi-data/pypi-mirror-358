import unittest
from unittest import mock
import django
from io import StringIO
from django.core.management import call_command
from django.urls import re_path
from django.http import HttpResponse
import os


urlpatterns = []


class RestClientTestCase(unittest.TestCase):

    def setUp(self):
        import warnings
        warnings.filterwarnings("ignore", category=DeprecationWarning)
        os.environ["DJANGO_SETTINGS_MODULE"] = "tests.mock_settings"
        from django.conf import settings
        self.setup_settings(settings)
        django.setup()

        from rest_framework.decorators import api_view

        from sparrow_cloud.apps.schema_command.schemas import patch_apiview_schema
        patch_apiview_schema()

        @api_view()
        def detail(request, question_id):
            return HttpResponse("You're looking at question %s." % question_id)

        urlpatterns.extend([
            re_path(r'^/ssss/xxx/$', detail),
            re_path(r'^/ssuuu/xxddx/$', detail),
        ]
        )

    @mock.patch('sparrow_cloud.restclient.rest_client.post', return_value={})
    def test_register_schema_command(self, mock_post):
        out = StringIO()
        # os.environ["SCHEMA_SERVICE_HOST"] = "127.0.0.1:8001"
        call_command('register_api_schema', '-p', stdout=out)
        r = out.read()
        print(r)
        self.assertEqual(r, '')

    def tearDown(self):
        # del os.environ["SCHEMA_SERVICE_HOST"]
        pass

    def setup_settings(self, settings):
        settings.XX = "1"
        settings.SECRET_KEY = "ss"
        settings.ROOT_URLCONF = __name__

        # settings.SPARROW_SCHEMA_REGISTER_CONF = {
        #     "SCHEMA_SERVICE": "xxxxx-svc:8001",
        #     "API_PATH": "/api/schema_i/register/"
        # }
        settings.SERVICE_CONF = {
            "NAME": "schema"
        }
        # settings.CONSUL_CLIENT_ADDR = {
        #     "HOST": os.environ.get("CONSUL_IP", "127.0.0.1"),  # 在k8s上的环境变量类型：变量/变量引用
        #     "PORT": os.environ.get("CONSUL_PORT", 8500)
        # }
