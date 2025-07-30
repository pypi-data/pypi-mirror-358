import jwt
import os
import time
import unittest

JWT_SECRET = "hard_to_guess_string"
USER_ID = 'abcedfg1234567'

# # 有效的对称加密token
# class MockRequest(object):
#     def __init__(self):
#         self.META = {"HTTP_AUTHORIZATION": self.get_token()}

#     def get_token(self):
#         payload = {"uid": USER_ID,
#                 "app_id": "app_0000",
#                 "exp": int(time.time()+60*60),
#                 "iat": int(time.time()),
#                 "iss": "test"
#             }
#         return b'Token '+jwt.encode(payload, JWT_SECRET, algorithm='HS256')

# # 过期无效的对称加密token
# class MockInvalidRequest(object):
#     def __init__(self):
#         self.META = {"HTTP_AUTHORIZATION": self.get_token()}

#     def get_token(self):
#         payload = { "uid": USER_ID,
#                 "app_id": "app_0000",
#                 "exp": int(time.time()-100),
#                 "iat": int(time.time()-500),
#                 "iss": "test"
#             }
#         return b'Token '+jwt.encode(payload, JWT_SECRET, algorithm='HS256')

# 有效的非对称加密token


class MockAsyRequest(object):
    def __init__(self):
        self.META = {"HTTP_AUTHORIZATION": self.get_token()}

    def get_token(self):
        payload = {"uid": USER_ID,
                   "app_id": "app_0000",
                   "exp": int(time.time()+60*60),
                   "iat": int(time.time()),
                   "iss": "test"
                   }
        private_key_path = os.getenv("PRIVATE_KEY_PATH")
        if private_key_path is None:
            raise ValueError(
                "Environment variable PRIVATE_KEY_PATH is not set")

        with open(private_key_path, "r", encoding="UTF-8") as private_file:
            private_key = private_file.read()
        token = "Token " + jwt.encode(payload, private_key, algorithm='RS256')
        return bytes(token, encoding="utf8")

# 过期无效的非对称加密token


class MockInvalidAsyRequest(object):
    def __init__(self):
        self.META = {"HTTP_AUTHORIZATION": self.get_token()}

    def get_token(self):
        payload = {"uid": USER_ID,
                   "app_id": "app_0000",
                   "exp": int(time.time()-100),
                   "iat": int(time.time()-500),
                   "iss": "test"
                   }
        # private_key = open(os.getenv("PRIVATE_KEY_PATH")).read()
        private_key_path = os.getenv("PRIVATE_KEY_PATH")
        if private_key_path is None:
            raise ValueError(
                "Environment variable PRIVATE_KEY_PATH is not set")

        with open(private_key_path, "r", encoding="UTF-8") as private_file:
            private_key = private_file.read()
        token = "Token " + jwt.encode(payload, private_key, algorithm='RS256')
        return bytes(token, encoding="utf8")

# 空token


class MockEmptyRequest(object):
    def __init__(self):
        self.META = {"HTTP_AUTHORIZATION": b'token '}


class TestJWTMiddleware(unittest.TestCase):

    def setUp(self):
        os.environ.setdefault("JWT_SECRET", JWT_SECRET)
        os.environ.setdefault("PRIVATE_KEY_PATH", "./tests/rsa_private.pem")
        # 设置环境变量 SC_JWT_PUBLIC_KEY，如果没有设置则读取并设置
        if "SC_JWT_PUBLIC_KEY" not in os.environ:
            with open("./tests/rsa_public.pem", "r", encoding="UTF-8") as public_file:
                os.environ["SC_JWT_PUBLIC_KEY"] = public_file.read()

    def test_asy_token(self):
        '''
        测试非对称加密
        '''
        from sparrow_cloud.middleware.jwt_middleware import JWTMiddleware
        request = MockAsyRequest()
        JWTMiddleware().process_request(request)
        self.assertIn("REMOTE_USER", request.META)
        self.assertIn("payload", request.META)
        self.assertIn("X-Jwt-Payload", request.META)
        self.assertEqual(USER_ID, request.META.get("REMOTE_USER"))
        self.assertIsNotNone(request.META.get("payload"))

    def test_invalid_asy_token(self):
        '''
        测试过期无效的非对称加密
        '''
        from sparrow_cloud.middleware.jwt_middleware import JWTMiddleware
        request = MockInvalidAsyRequest()
        JWTMiddleware().process_request(request)
        self.assertIn("REMOTE_USER", request.META)
        self.assertIn("payload", request.META)
        self.assertNotIn("X-Jwt-Payload", request.META)
        self.assertIsNone(request.META.get("REMOTE_USER"))
        self.assertIsNone(request.META.get("payload"))

    def test_empty_auth_token(self):
        '''
        测试携带空的token
        '''
        from sparrow_cloud.middleware.jwt_middleware import JWTMiddleware
        request = MockEmptyRequest()
        JWTMiddleware().process_request(request)
        self.assertIn("REMOTE_USER", request.META)
        self.assertIn("payload", request.META)
        self.assertNotIn("X-Jwt-Payload", request.META)
        self.assertIsNone(request.META.get("REMOTE_USER"))
        self.assertIsNone(request.META.get("payload"))


if __name__ == '__main__':
    unittest.main()
