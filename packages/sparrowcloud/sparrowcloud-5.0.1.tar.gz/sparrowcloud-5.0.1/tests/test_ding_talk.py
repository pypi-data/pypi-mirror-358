# import os
# import unittest
# from unittest import mock
# from sparrow_cloud.restclient.exception import HTTPException
# from django.test import RequestFactory
# from sparrow_cloud.dingtalk.sender import send_message


# MOCK_RESPONSE = {"data": {"code": 0, "message": "success"}}

# RESPONSE_CONTENT = {
#     "group_code_list": [
#         "group_code_list 传递错误"
#     ]
# }

# XX = HTTPException(
#             code="http_exception",
#             detail=RESPONSE_CONTENT,
#         )
# XX.status_code = 400


# MOCK_RESPONSE_400 = XX


# def mocked_requests(*args, **kwargs):
#     class MockResponse:
#         def __init__(self, json_data, status_code, content):
#             self.json_data = json_data
#             self.status_code = status_code
#             self.content = content

#         def json(self):
#             return self.json_data
#     return MockResponse(json_data=None, content={"code": 0, "message": "success"},  status_code=200)


# class TestSendMessage(unittest.TestCase):
#     """test 钉钉机器人 client"""
#     rf = RequestFactory()

#     def setUp(self):
#         os.environ["DJANGO_SETTINGS_MODULE"] = "tests.mock_settings"

#     @mock.patch('sparrow_cloud.restclient.rest_client.post', return_value=MOCK_RESPONSE)
#     def test_send_message(self, request):
#         res = send_message("test", ["123"], "wechat", "text")
#         self.assertEqual(res.get("data"), {"code": 0, "message": "success"})

#     @mock.patch('sparrow_cloud.restclient.rest_client.post', return_value=XX)
#     def test_send_message_400(self, request):
#         self.assertEqual(send_message("test", ["123"], "wechat", "text").status_code, 400)
#         self.assertEqual(send_message("test", ["123"], "wechat", "text").detail, XX.detail)

#     @mock.patch('sparrow_cloud.restclient.rest_client.post', return_value=XX)
#     def test_send_message_typeerror(self, request):
#         try:
#             send_message(1, {})
#         except Exception as ex:
#             self.assertEqual(type(ex), TypeError)
