# import logging
# from unittest.mock import Mock
# from django.test import TestCase
# from sparrow_cloud.utils import local
# from sparrow_cloud.filter.log_filters import RequestIDFilter


# class RequestIDFilterTestCase(TestCase):
#     def setUp(self):
#         self.filter = RequestIDFilter()
#         self.log_record = Mock(spec=logging.LogRecord)

#     def test_filter_with_request_id(self):
#         local.request_id = '12345'
#         self.assertTrue(self.filter.filter(self.log_record))
#         self.assertEqual(self.log_record.request_id, '12345')

#     def test_filter_without_request_id(self):
#         del local.request_id
#         self.assertTrue(self.filter.filter(self.log_record))
#         self.assertEqual(self.log_record.request_id, 'HTTP_X_REQUEST_ID')
