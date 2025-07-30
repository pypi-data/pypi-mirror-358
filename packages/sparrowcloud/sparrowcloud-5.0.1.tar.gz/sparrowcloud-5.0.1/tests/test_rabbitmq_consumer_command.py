import os
import unittest
from io import StringIO
from unittest import mock

import django
import pika
from django.urls import re_path
from django.core.management import call_command
from django.http import HttpResponse

from sparrow_cloud.apps.message_service.management.commands._controller import RabbitMQConsumer


def task(*args, **kwargs):
    # print('*' * 10)
    pass


def detail(request, question_id):
    return HttpResponse("You're looking at question %s." % question_id)


urlpatterns = [
    re_path(r'^/ssss/xxx/$', detail),
    re_path(r'^/ssuuu/xxddx/$', detail),
]


class RestClientTestCase(unittest.TestCase):

    def setUp(self):
        # os.environ["SPARROW_BROKER_HOST"] = "127.0.0.1:8001"
        # os.environ["SPARROW_BACKEND_HOST"] = "127.0.0.1:8002"
        os.environ["DJANGO_SETTINGS_MODULE"] = "tests.mock_settings"

    # @mock.patch(
    #     'sparrow_cloud.apps.message_service.management.commands._sparrow_rabbitmq_consumer.RabbitMQConsumer.target_func_map',
    #     return_value='tests.test_rabbitmq_consumer_command.task')
    # @mock.patch('sparrow_cloud.apps.message_service.management.commands._sparrow_rabbitmq_consumer.RabbitMQConsumer.consume',
    #             return_value='接收任务成功')
    # def test_consumer_command(self, mock_target_func_map, mock_consume):
    #     from django.conf import settings
    #     self.setup_settings(settings)
    #     django.setup()
    #     out = StringIO()
    #     call_command('rabbitmq_consumer', '--queue', 'QUEUE_CONF', stdout=out)
    #     self.assertEqual(out.read(), '')

    def setup_settings(self, settings):
        settings.XX = "1"
        # settings.SECRET_KEY = "ss"
        # settings.SPARROW_RABBITMQ_CONSUMER_CONF = {
        #     "MESSAGE_BROKER_CONF": {
        #         "USER_NAME": "test_name",
        #         "PASSWORD": "test_password",
        #         "VIRTUAL_HOST": "test_virtual",
        #         "BROKER_SERVICE_CONF": "sparrow-test:8001",
        #     },
        #     "MESSAGE_BACKEND_CONF": {
        #         "BACKEND_SERVICE_CONF": "sparrow-test:8001",
        #         "API_PATH": "/api/sparrow_test/task/test_update/"
        #     }
        # }

        settings.QUEUE_CONF = {
            "QUEUE": "TEST_QUEUE",
            "TARGET_FUNC_MAP": {
                "ORDER_PAY_SUC_ONLINE": "./task",
            }
        }
        settings.ROOT_URLCONF = __name__


mock_message_broker_conf = {
    "host": "127.0.0.1",
    "port": 8001,
    "username": "username",
    "password": "password",
    "virtual_host": "virtual_host",
}

mock_test_queue_conf_1 = {
    "QUEUE": "",
    "TARGET_FUNC_MAP": {
        "ORDER_PAY_SUC_ONLINE": "path",
    },
}

mock_base64_to_json = {
    'name': '',
    'args': (),
    'kwargs': {}
}


class MockPikaConnection:

    def add_callback_threadsafe(self, callback):
        pass

    def channel(self):
        return MockChannel()


class MockChannel:

    def basic_qos(self, prefetch_count, *args, **kwargs):
        pass

    def basic_consume(self, *args, **kwargs):
        pass

    def start_consuming(self):
        # print('start_consuming...')
        pass

    def stop_consuming(self):
        # print('stop_consuming...')
        pass


"""
无法assert异常错误
只能通过设定不同参数尽可能覆盖到代码行确保判断, try等都正常运行
===passed===
"""


class DoWorkTestCase(unittest.TestCase):

    def setUp(self):
        os.environ["DJANGO_SETTINGS_MODULE"] = "tests.mock_settings"
        from django.conf import settings
        settings.ROOT_URLCONF = __name__
        django.setup()

    @mock.patch('sparrow_cloud.apps.message_service.management.commands._controller.rest_client.post',
                return_value='ok')
    @mock.patch(
        'sparrow_cloud.apps.message_service.management.commands._controller.pika.BlockingConnection.add_callback_threadsafe',
        return_value='')
    def test_mq_consumer_contrl_do_work(self, rest_client_post, add_callback_threadsafe):
        consumer = RabbitMQConsumer(
            queue='TEST_QUEUE',
            message_broker_conf=mock_message_broker_conf,
        )
        connection = MockPikaConnection()
        # channel = connection.channel()
        method_frame = pika.spec.Basic.Deliver()
        header_frame = pika.spec.BasicProperties()
        header_frame.headers = {'task_id': '1234'}

        # base64_to_json 参数为bytes, 参数异常被捕获
        consumer.do_work(connection, None, method_frame, header_frame, 123)
        consumer.do_work(connection, None, method_frame, header_frame, b'')
        # _get_jstr_from_cls 的 result 为 false
        with mock.patch(
                'sparrow_cloud.apps.message_service.management.commands._sparrow_rabbitmq_consumer.RabbitMQConsumer._get_jstr_from_cls',
                return_value=(False, '')) as mock_get_jstr_from_cls:
            consumer.do_work(connection, None, method_frame, header_frame, b'')
        # _get_jstr_from_cls 的 result 为 true
        with mock.patch(
                'sparrow_cloud.apps.message_service.management.commands._sparrow_rabbitmq_consumer.RabbitMQConsumer._get_jstr_from_cls',
                return_value=(True, '')) as mock_get_jstr_from_cls:
            consumer.do_work(connection, None, method_frame, header_frame, b'')
        # 异常错误
        with mock.patch(
                'sparrow_cloud.apps.message_service.management.commands._sparrow_rabbitmq_consumer.RabbitMQConsumer._get_jstr_from_cls',
                side_effect=KeyError('foo')) as mock_get_jstr_from_cls:
            consumer.do_work(connection, None, method_frame, header_frame, b'')

    @mock.patch(
        'sparrow_cloud.apps.message_service.management.commands._sparrow_rabbitmq_consumer.RabbitMQConsumer.target_func_map',
        side_effect=task)
    @mock.patch(
        'sparrow_cloud.apps.message_service.management.commands._controller.pika.BlockingConnection',
        return_value=MockPikaConnection())
    def test_mq_consumer_conmmand(self, rest_client_post, add_callback_threadsafe):
        consumer = RabbitMQConsumer(
            queue='TEST_QUEUE',
            message_broker_conf=mock_message_broker_conf,
        )
        consumer.consume()

        # pika.exceptions.ConnectionClosedByBroker. try again later
        with mock.patch(
                'sparrow_cloud.apps.message_service.management.commands._controller.pika.PlainCredentials',
                side_effect=pika.exceptions.ConnectionClosedByBroker(1, 'ConnectionClosedByBroker')):
            try:
                consumer.consume()
            except Exception as e:
                self.assertEqual(
                    'pika.exceptions.ConnectionClosedByBroker. try again later', e.__str__())

        # pika.exceptions.AMQPChannelError. try again later
        with mock.patch(
                'sparrow_cloud.apps.message_service.management.commands._controller.pika.PlainCredentials',
                side_effect=pika.exceptions.AMQPChannelError('AMQPChannelError')):
            try:
                consumer.consume()
            except Exception as e:
                self.assertEqual(
                    'pika.exceptions.AMQPChannelError. try again later', e.__str__())

        # broker connection error:AMQPConnectionError: ('BrokerConnectonException',). try again later
        with mock.patch(
                'sparrow_cloud.apps.message_service.management.commands._controller.pika.PlainCredentials',
                side_effect=pika.exceptions.AMQPConnectionError('BrokerConnectonException')):
            try:
                consumer.consume()
            except Exception as e:
                self.assertEqual(
                    "broker connection error:AMQPConnectionError: ('BrokerConnectonException',). try again later", e.__str__())

        # Exception
        # rabbitmq consumer接收到异常，错误消息为Exception
        with mock.patch(
                'sparrow_cloud.apps.message_service.management.commands._controller.pika.PlainCredentials',
                side_effect=Exception('Exception')):
            try:
                consumer.consume()
            except Exception as e:
                self.assertEqual(
                    'rabbitmq consumer接收到异常，错误消息为Exception', e.__str__())
