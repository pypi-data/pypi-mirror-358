from sparrow_cloud.middleware.base.base_middleware import MiddlewareMixin
from sparrow_cloud.utils import local

class RequestIDMiddleware(MiddlewareMixin):
    def process_request(self, request):
        path = request.META.get("PATH_INFO")
        # 测活API不根据request_id生成
        if path == "/api/ping/i/":
            return
        else:
            # istio-proxy透传的request_id
            request_id = request.META.get('HTTP_X_REQUEST_ID')
            # 将request_id 存储到每个线程开辟的独立的空间，自定义log_filter使用
            local.request_id = request_id
            # 把request_id 透传到业务业务逻辑层
            request.id = request_id

    def process_response(self, request, response):
        path = request.META.get("PATH_INFO")
        if path == "/api/ping/i/":
            return response
        try:
            # 请求结束，删除线程request_id
            del local.request_id
        except AttributeError:
            pass
        return response