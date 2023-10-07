import jwt
import datetime
from util.yaml_util import read_yaml


def create_token(user_id, day=14):
    """
    :param user_id: 用户id
    :param day:  日期。单位天 ，默认14天
    :return:     生成的token
    """
    # 构造header
    headers = {
        'typ': 'jwt',
        'alg': 'HS256'
    }
    # 构造payload，根据需要自定义用户内容
    payload = {
        'user_id': user_id,  # 自定义用户ID
        'exp': datetime.datetime.utcnow() + datetime.timedelta(days=day)  # 默认14天有效
    }
    # 密钥
    SALT = read_yaml('token_private_key', 'config.yaml')
    token = jwt.encode(payload=payload, key=SALT, algorithm="HS256", headers=headers)
    return token
