import logging
import traceback
# from sparrow_cloud.dingtalk.sender import send_message
from sparrow_cloud.middleware.base.base_middleware import MiddlewareMixin
from sparrow_cloud.utils.get_settings_value import get_settings_value, get_service_name
from sparrow_cloud.utils.send_alert import send_feishu_post_notice

logger = logging.getLogger(__name__)

class ExceptionMiddleware(MiddlewareMixin):
    '''
    异常处理中间件，发生异常发送飞书消息
    需要配置SC_EXCEPTION_WEBHOOK环境变量
    '''
    def process_exception(self, request, exception):
        debug = get_settings_value("DEBUG")
        service_name = get_service_name()
        if not debug:
            exception_info = traceback.format_exc()
            send_feishu_post_notice(service_name, "异常中间件ExceptionMiddleware", exception_info)