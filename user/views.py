from django.http import JsonResponse
from rest_framework.decorators import api_view
from django.views.decorators.csrf import csrf_exempt
from .models import User
from drf_yasg2 import openapi
from drf_yasg2.utils import swagger_auto_schema
from rest_framework.views import APIView
import json, jwt, time, re, logging, hashlib
from util.yaml_util import read_yaml
from util.token_util import check_token
from util.creat_token_util import create_token


class UserView(APIView):
    request_body = openapi.Schema(
        type=openapi.TYPE_OBJECT,
        required=['phone', 'password'],
        properties={
            'phone': openapi.Schema(type=openapi.TYPE_STRING, description='手机号'),
            'password': openapi.Schema(type=openapi.TYPE_STRING, description='密码')
        })
    access_response_schema = openapi.Response(
        description='Successful response',
        schema=openapi.Schema(type=openapi.TYPE_OBJECT, properties={
            'code': openapi.Schema(type=openapi.TYPE_INTEGER, description='code'),
            'message': openapi.Schema(type=openapi.TYPE_STRING, description='message'),
            'data': openapi.Schema(type=openapi.TYPE_OBJECT, description='data', properties={
                'user_id': openapi.Schema(type=openapi.TYPE_INTEGER, description='id'),
                'username': openapi.Schema(type=openapi.TYPE_STRING, description='昵称'),
                'phone': openapi.Schema(type=openapi.TYPE_STRING, description='手机号'),
                'token': openapi.Schema(type=openapi.TYPE_STRING, description='token'),
            }),
        })
    )

    def __init__(self, **kwargs):
        super().__init__(kwargs)
        self.META = None
        self.body = None

    @swagger_auto_schema(value='/api/user/register', method='post', operation_summary='注册接口', request_body=request_body, responses={0: access_response_schema, 201: 'None'})
    @csrf_exempt
    @api_view(['POST'])
    def register(self):
        data = json.loads(self.body.decode('utf-8'))
        if data.get('phone') is None or data.get('password') is None:
            logging.error('参数缺少')
            Response = {
                "code": 10010,
                "message": "参数缺少"
            }
        else:
            phone = data['phone']
            password = data['password']
            if password == '' or phone == '':
                logging.error('请输入手机号和密码')
                Response = {
                    "code": 10003,
                    "message": "请输入手机号和密码"
                }
            else:
                if not re.match('^(13|14|15|16|17|18)[0-9]{9}$', str(phone)):
                    logging.error('不是合法手机号码')
                    Response = {
                        "code": 10001,
                        "message": "不是合法手机号码"
                    }
                else:
                    if not re.match('^(?![0-9]+$)(?![a-zA-Z]+$)[0-9A-Za-z]{6,16}$', str(password)):
                        logging.error('以字母开头，长度在6~18之间，只能包含字母、数字和下划线')
                        Response = {
                            "code": 10004,
                            "message": "以字母开头，长度在6~18之间，只能包含字母、数字和下划线"
                        }
                    else:
                        if (User.objects.filter(phone=phone)).count():
                            Response = {
                                "code": 10002,
                                "message": "该手机号已被注册"
                            }
                            logging.error('该手机号已被注册')
                        else:
                            Encry = hashlib.md5()  # 实例化md5
                            Encry.update(password.encode('utf-8'))  # 字符串字节加密
                            password = Encry.hexdigest()  # 字符串加密
                            User.objects.create(phone=phone, username=phone, password=password)
                            data = User.objects.get(phone=phone)
                            data.save()
                            data.token = create_token(user_id=User.objects.get(phone=phone).id)
                            logging.info('注册成功')
                            Response = {
                                "code": 0,
                                "message": "注册成功",
                                "data": {
                                    "user_id": data.id,
                                    "username": data.username,
                                    "phone": str(data.phone.replace(phone[3:7], '****')),
                                    "token": str(data.token)
                                }
                            }
        return JsonResponse(Response)

    @swagger_auto_schema(value='/api/user/login',method='post', operation_summary='登录接口', request_body=request_body, responses={0: access_response_schema, 201: 'None'})
    @csrf_exempt
    @api_view(['POST'])
    def login(self):
        data = json.loads(self.body.decode('utf-8'))
        if data.get('phone') is None or data.get('password') is None:
            logging.error('参数缺少')
            Response = {
                "code": 10010,
                "message": "参数缺少"
            }
        else:
            phone = data['phone']
            password = data['password']
            if password == '' or phone == '':
                logging.error('请输入手机号和密码')
                Response = {
                    "code": 10003,
                    "message": "请输入手机号和密码"
                }
            else:
                if not (User.objects.filter(phone=phone)).count():
                    logging.error('该手机号没有注册')
                    Response = {
                        "code": 10005,
                        "message": "该手机号没有注册"
                    }
                else:
                    Encry = hashlib.md5()  # 实例化md5
                    Encry.update(password.encode('utf-8'))  # 字符串字节加密
                    password = Encry.hexdigest()  # 字符串加密
                    data = User.objects.get(phone=phone)
                    if data.password != password:
                        logging.error('密码错误')
                        Response = {
                            "code": 10006,
                            "message": "密码错误"
                        }
                    else:
                        data.token = create_token(user_id=data.user_id)
                        data.save()
                        logging.info('登录成功')
                        Response = {
                            "code": 0,
                            "message": "登录成功",
                            "data": {
                                "user_id": data.id,
                                "username": data.username,
                                "phone": str(data.phone.replace(phone[3:7], '****')),
                                "token": str(data.token)
                            }
                        }
        return JsonResponse(Response)

    change_password_request_body = openapi.Schema(
        type=openapi.TYPE_OBJECT,
        required=['user_id', 'old_password', 'password'],
        properties={
            'user_id': openapi.Schema(type=openapi.TYPE_INTEGER, description='user_id'),
            'old_password': openapi.Schema(type=openapi.TYPE_STRING, description='旧密码'),
            'password': openapi.Schema(type=openapi.TYPE_STRING, description='密码')
        })

    @swagger_auto_schema(value='/api/user/reset', method='post', operation_summary='修改密码接口', request_body=change_password_request_body, responses={0: access_response_schema, 201: 'None'})
    @csrf_exempt
    @api_view(['POST'])
    def change_password(self):
        data = json.loads(self.body.decode('utf-8'))
        if data.get('user_id') is None or data.get('old_password') is None or data.get('password') is None:
            logging.error('参数缺少')
            Response = {
                "code": 10010,
                "message": "参数缺少"
            }
        else:
            user_id = data['user_id']
            old_password = data['old_password']
            password = data['password']
            token = self.META.get('HTTP_AUTHORIZATION')
            Response = json.loads(check_token(token))
            if Response['code'] == 0:
                if old_password == '' or user_id == '' or password == '':
                    logging.error('参数缺少')
                    Response = {
                        "code": 10010,
                        "message": "参数缺少"
                    }
                else:
                    if not User.objects.get(id=user_id).token == token:
                        logging.error('别用别人的token')
                        Response = {
                            "code": 10008,
                            "message": "别用别人的token"
                        }
                    else:
                        Encry_old_password = hashlib.md5()  # 实例化md5
                        Encry_old_password.update(old_password.encode('utf-8'))  # 字符串字节加密
                        old_password = Encry_old_password.hexdigest()  # 字符串加密
                        Encry_password = hashlib.md5()  # 实例化md5
                        Encry_password.update(password.encode('utf-8'))  # 字符串字节加密
                        password = Encry_password.hexdigest()  # 字符串加密
                        data = User.objects.get(id=user_id)
                        if data.password != old_password:
                            logging.error('旧密码错误')
                            Response = {
                                "code": 10014,
                                "message": "旧密码错误"
                            }
                        else:
                            data.password = password
                            data.token = create_token(user_id=data.user_id)
                            data.save()
                            logging.info('修改密码成功')
                            Response = {
                                "code": 0,
                                "message": "修改密码成功",
                                "data": {
                                    "user_id": data.id,
                                    "username": data.username,
                                    "phone": str(data.phone.replace(data.phone[3:7], '****')),
                                    "token": str(data.token)
                                }
                            }
        return JsonResponse(Response)
