import logging
from sparrow_cloud.utils import local

class RequestIDFilter(logging.Filter):

    def filter(self, record):
        # 拿线程中的request_id，自定义日志格式
        record.request_id = getattr(local, 'request_id', "HTTP_X_REQUEST_ID")
        return True