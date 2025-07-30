import os
import unittest
from unittest import mock
from sparrow_cloud.middleware.exception import ExceptionMiddleware

class MockRequest(object):
    META = {}

class MockException(Exception):
    def __str__(self):
        return "mock异常处理中间件"

class TestExceptionMiddleware(unittest.TestCase):

    def setUp(self):
        os.environ["DJANGO_SETTINGS_MODULE"] = "tests.mock_settings"
        self.middleware = ExceptionMiddleware()

    @mock.patch('sparrow_cloud.utils.send_alert.requests.post', return_value={"code":0})
    def test_none_exception(self,mock_request):
        self.assertEqual(self.middleware.process_exception(MockRequest(),None),None)

    @mock.patch('sparrow_cloud.utils.send_alert.requests.post', return_value={"code":0})
    def test_exception_no_webhook(self,mock_request):
        self.assertEqual(os.getenv("SC_EXCEPTION_WEBHOOK"), None)
        self.assertEqual(self.middleware.process_exception(MockRequest(),MockException()),None)

    @mock.patch('sparrow_cloud.utils.send_alert.requests.post', return_value={"code":0})
    def test_exception_with_webhook(self,mock_request):
        os.environ.setdefault("SC_EXCEPTION_WEBHOOK","http://test.feishu.com/webhook/mock")
        self.assertEqual(self.middleware.process_exception(MockRequest(),MockException()),None)

    @mock.patch('sparrow_cloud.utils.send_alert.requests.post', side_effect=Exception("发送超时"))
    def test_exception_send_excepiton(self,mock_request):
        os.environ.setdefault("SC_EXCEPTION_WEBHOOK","http://test.feishu.com/webhook/mock")
        self.assertEqual(self.middleware.process_exception(MockRequest(),MockException()),None)
