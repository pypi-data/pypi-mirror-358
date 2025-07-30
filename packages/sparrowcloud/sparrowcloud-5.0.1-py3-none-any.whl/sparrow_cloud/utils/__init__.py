try:
    from asgiref.local import Local
except ImportError:
    from threading import local as Local

# 为每个线程开辟一个独立的空间进行数据存储
local = Local()