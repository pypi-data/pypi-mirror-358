import requests
import logging
import json
import os

logger = logging.getLogger(__name__)

def send_feishu_notice(data:str):
    '''
    发送飞书文本通知消息
    '''
    webhook_url = os.environ.get("SC_EXCEPTION_WEBHOOK", None)
    if not webhook_url:
        logger.warning(f"未获取到异常通知SC_EXCEPTION_WEBHOOK环境变量，未发送通知消息{data}")
        return
    feishu_data = {"msg_type":"text","content":{"text":data}}
    try:#data=json.dumps(feishu_data)
        requests.post(webhook_url, json=feishu_data, timeout=10, headers={'Content-Type':'application/json'})
    except Exception as e:
        logger.info(f"发送通知消息发生异常：{e.__str__()}，发送数据为{data}")

def send_feishu_post_notice(title, src, data:str):
    '''
    发送飞书富文本消息
    :title 富文本消息的标题
    :src 消息的来源，用户提醒用户消息来源
    :data 消息内容
    '''
    webhook_url = os.environ.get("SC_EXCEPTION_WEBHOOK", None)
    if not webhook_url:
        logger.warning(f"未获取到异常通知SC_EXCEPTION_WEBHOOK环境变量，未发送通知消息{data}")
        return
    feishu_data = {
        "msg_type": "post",
        "content": {
            "post": {
                "zh_cn": {
                    "title": title,
                    "content": [
                        [
                            {
                                "tag": "text",
                                "text": src
                            }
                        ],
                        [
                            {
                                "tag": "text",
                                "text": data
                            }
                        ]
                    ]
                }
            }
        }
    }
    try:
        requests.post(webhook_url, json=feishu_data, timeout=10, headers={'Content-Type':'application/json'})
    except Exception as e:
        logger.info(f"发送通知消息发生异常：{e.__str__()}，发送数据为{data}")