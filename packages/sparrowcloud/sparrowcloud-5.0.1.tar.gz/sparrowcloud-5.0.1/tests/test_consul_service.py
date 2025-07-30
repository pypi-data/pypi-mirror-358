# import os
# import unittest
# from unittest import mock
# from sparrow_cloud.registry.service_discovery import consul_service
# from django.core.exceptions import ImproperlyConfigured
#
# # 与 SPARROW_SERVICE_REGISTER_NAME 对应的 _HOST
# SPARROW_SERVICE_REGISTER_NAME_HOST = "162.23.7.247:8001"
#
#
# SERVICE_CONF = {
#     "ENV_NAME": "PERMISSION_REGISTER_NAME_HOST",
#     "VALUE": "sprrow-permission-svc"
#     }
#
#
# CONSUL_RETURN_DATA = (
#     "name",
#     [
#         {'ServiceAddress': '162.23.7.247', 'ServicePort': 8001},
#         {'ServiceAddress': '142.27.4.252', 'ServicePort': 8001},
#         {'ServiceAddress': '122.21.8.131', 'ServicePort': 8001},
#     ]
# )
#
# CONSUL_RETURN_DATA1 = (
#     "name",
#     []
# )
#
#
# class ConsulServiceTest(unittest.TestCase):
#
#     def setUp(self):
#         os.environ["DJANGO_SETTINGS_MODULE"] = "tests.mock_settings"
#
#     @mock.patch('consul.Consul.Catalog.service', return_value=CONSUL_RETURN_DATA)
#     def test_consul_parameter_variable(self, mock_consul_service):
#         """
#         测试未设置环境变量
#         """
#         from django.conf import settings
#         os.environ["PERMISSION_REGISTER_NAME_HOST"] = ""
#         settings.CONSUL_CLIENT_ADDR = {
#             "HOST": "127.0.0.1",
#             "PORT": 8500
#         }
#         settings.SERVICE_CONF = SERVICE_CONF
#         expect_result_list = ['{}:{}'.format(
#             _["ServiceAddress"], _['ServicePort']) for _ in CONSUL_RETURN_DATA[1]]
#         addr = consul_service(SERVICE_CONF)
#         self.assertEqual(addr in expect_result_list, True)
#
#     @mock.patch('consul.Consul.Catalog.service', return_value=CONSUL_RETURN_DATA)
#     def test_consul_parameter_no_variable(self, mock_consul_service):
#         """
#         测试设置环境变量:
#         os.environ["SPARROW_SERVICE_REGISTER_NAME_HOST"] = "127.0.0.1:8001"
#         """
#         from django.conf import settings
#         os.environ["PERMISSION_REGISTER_NAME_HOST"] = "127.0.0.1:8001"
#         settings.CONSUL_CLIENT_ADDR = {
#             "HOST": "127.0.0.1",
#             "PORT": 8500
#         }
#         settings.SERVICE_CONF = SERVICE_CONF
#         addr = consul_service(SERVICE_CONF)
#         self.assertEqual(addr, '127.0.0.1:8001')
#
#     @mock.patch('consul.Consul.Catalog.service', return_value=CONSUL_RETURN_DATA1)
#     def test_consul_service_empty_list(self, mock_consul_service):
#         """
#         测试未设置环境变量
#         """
#         from django.conf import settings
#         os.environ["PERMISSION_REGISTER_NAME_HOST"] = ""
#         settings.CONSUL_CLIENT_ADDR = {
#             "HOST": "127.0.0.1",
#             "PORT": 8500
#         }
#         settings.SERVICE_CONF = SERVICE_CONF
#         try:
#             consul_service(SERVICE_CONF)
#         except ImproperlyConfigured as ex:
#             self.assertEqual(type(ex), ImproperlyConfigured)
#
#     def tearDown(self):
#         del os.environ["DJANGO_SETTINGS_MODULE"]
