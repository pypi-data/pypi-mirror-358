from django.test import RequestFactory, TestCase
from sparrow_cloud.utils import local
from sparrow_cloud.middleware.log_middleware import RequestIDMiddleware


class RequestIDMiddlewareTestCase(TestCase):
    def setUp(self):
        self.middleware = RequestIDMiddleware()
        self.factory = RequestFactory()

    def test_request_id_set(self):
        request = self.factory.get('/test/')
        request.META['HTTP_X_REQUEST_ID'] = '12345'
        self.middleware.process_request(request)
        self.assertEqual(request.id, '12345')
        self.assertEqual(local.request_id, '12345')

    def test_request_id_not_set(self):
        request = self.factory.get('/api/ping/i/')
        self.middleware.process_request(request)
        self.assertIsNone(request.META.get('HTTP_X_REQUEST_ID'))

    def test_response(self):
        request = self.factory.get('/test/')
        response = self.middleware.process_response(request, None)
        self.assertIsNone(response)

    def test_request_id_deleted(self):
        request = self.factory.get('/test/')
        request.META['HTTP_X_REQUEST_ID'] = '12345'
        self.middleware.process_request(request)
        self.assertIsNotNone(local.request_id)
        self.middleware.process_response(request, None)
        with self.assertRaises(AttributeError):
            local.request_id
