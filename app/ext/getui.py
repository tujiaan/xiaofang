import time
from _sha256 import sha256
from pprint import pprint

import requests
from flask import json

from instance import config


class Getui(object):
    appkey = None
    mastersecret = None
    appid = None
    authtoken = None
    _expire_time = None

    def __init__(self, app=None):
        self.app = app
        if app is not None:
            self.init_app(app)

    def init_app(self, app):
        self.app = app
        config = app.config.copy()
        self.appkey = config.get('APP_KEY')
        self.mastersecret = config.get('MASTER_SECRET')
        self.appid = config.get('APP_ID')

    @property
    def sign(self):
        now=int(time.time() * 1000)
        if self.authtoken is not None:
            if self._expire_time > now+10000:

                return self.authtoken
        print(self.appkey, self.mastersecret)
        sign = sha256((self.appkey + str(now) + self.mastersecret).encode())
        url = 'https://restapi.getui.com/v1/'+str(self.appid)+'/auth_sign'
        data = {
            "sign": sign.hexdigest(),
            "timestamp":str(now),
            "appkey": self.appkey
        }
        res = requests.post(url=url, json=data).json()
        if res.get('result') == 'ok':
            self._expire_time = int(res.get('expire_time','0'))
            self.authtoken = res.get('auth_token')

        return self.authtoken

    def getAuth(self):
        pprint(self.sign)
        now = int(time.time() * 1000)
        url = 'https://restapi.getui.com/v1/'+str(self.appid)+'/auth_sign'
        data = {
            "sign": self.sign,
            "timestamp":str(now),
            "appkey": self.appkey
        }
        res = requests.post(url=url, json=data)
        result = (res.json()).get('auth_token')
        return result, 200

    def bind(self, userid, cid):
        headers = {
            'Content-Type': 'application/json',
            'authtoken': self.sign
        }
        url = 'https://restapi.getui.com/v1/'+str(self.appid)+'/bind_alias'
        data = {
            "alias_list": [{"cid": cid, "alias": userid}]
        }
        res = requests.post(url=url, headers=headers, json=data)
        result = res.json()
        return result

    def getTaskId(self, message_id,  content):
        headers = {
            'Content-Type': 'application/json',
            'authtoken': self.sign
        }
        url = str('https://restapi.getui.com/v1/'+str(self.appid)+'/save_list_body')
        data = {
            "message": {
                   "appkey": self.appkey,
                   "is_offline": True,
                   "offline_expire_time": 10000000,
                   "msgtype": "notification"
                },
                "notification": {
                    "style": {
                        "type": 0,
                        "text": content,
                        "title": "消息推送"
                    },
                    "transmission_type": True,
                    "transmission_content":str(content+","+message_id)#json.dumps({"message_id": message_id, "content": content}) #str(json.dumps({"message_id": message_id, "content": content}))
                }
        }
        res = requests.post(url=url, headers=headers, json=data)
        return res.json().get('taskid')

    def sendList(self, alias, taskid):
        headers = {
            'Content-Type': 'application/json',
            'authtoken': str(self.sign)

        }
        url = str('https://restapi.getui.com/v1/'+str(self.appid)+'/push_list')
        data = {

            "alias": alias,
            "taskid": str(taskid),
            "need_detail": True
        }
        res = requests.post(url=url, headers=headers, json=data)
        return res.json()

    def unbind(self, userid, cid):
        url = str('https: // restapi.getui.com / v1 /' +str(self.appid)+'/ unbind_alias')
        headers = {
            'Content-Type': 'application/json',
            'authtoken': str(self.sign)
        }
        data = {
            "cid": cid,
            "alias": userid
        }
        res = requests.post(url=url, headers=headers, json=data)
        return res.json()



getui = Getui()