import json

from user.models import User
import logging


def check_token(token):
    if token is None or not User.objects.filter(token=token).count() or token == '':
        logging.error('您还未登录')
        Response = {
            "code": 10006,
            "message": "您还未登录"
        }
    else:
        Response = {
            "code": 0,
            "message": "token校验通过"
        }
    return json.dumps(Response)