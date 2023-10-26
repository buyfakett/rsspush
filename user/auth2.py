import jwt
from jwt import exceptions
from rest_framework.exceptions import AuthenticationFailed
from rest_framework.authentication import BaseAuthentication
from util.yaml_util import read_yaml
from .models import User

# 定义一个白名单 注册登录接口 随便访问
white_list = [
    '/api/docs/',
    '/admin/',
    '/api/docs/?format=openapi',
    '/api/user/register',
    '/api/user/login',
    '/api/push/refresh',
]


class JWTAuthentication(BaseAuthentication):
    def authenticate(self, request):
        # 密钥，必须跟签发token的一样
        salt = read_yaml('token_private_key', 'config.yaml')
        # 从请求头中获取token
        # 放的格式 Authorization:JWT xxxxxxxx
        token = request.META.get('HTTP_AUTHORIZATION')
        # 获取url
        url = request.get_full_path()
        # 判断url在不在白名单中
        if url not in white_list:
            if not token:
                raise AuthenticationFailed('没有携带token')
            try:
                # jwt提供了通过三段token，取出payload的方法，并且有校验功能
                # 这个是我们签发时，封装的payload字典
                verified_payload = jwt.decode(jwt=token, key=salt, verify=True)
            except exceptions.ExpiredSignatureError:
                raise AuthenticationFailed('token已失效')
            except jwt.DecodeError:
                raise AuthenticationFailed('token认证失败')
            except jwt.InvalidTokenError:
                raise AuthenticationFailed('非法的token')
            except Exception as e:
                # 所有异常都会走到这
                raise AuthenticationFailed(str(e))
            # 去数据库查出用户
            user = User.objects.get(id=verified_payload.get('user_id'))
            # 认证通过，返回token
            return user, token  # request.user/auth
        return
