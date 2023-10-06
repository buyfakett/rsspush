from django.http import JsonResponse
from rest_framework.decorators import api_view
from django.views.decorators.csrf import csrf_exempt
from .models import User
import re, logging, hashlib
from drf_yasg2 import openapi
from drf_yasg2.utils import swagger_auto_schema
from rest_framework.views import APIView
import json, jwt, time
from util.yaml_util import read_yaml


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
                'id': openapi.Schema(type=openapi.TYPE_INTEGER, description='id'),
                'username': openapi.Schema(type=openapi.TYPE_STRING, description='昵称'),
                'phone': openapi.Schema(type=openapi.TYPE_STRING, description='手机号'),
                'token': openapi.Schema(type=openapi.TYPE_STRING, description='token'),
            }),
        })
    )

    def __init__(self, **kwargs):
        super().__init__(kwargs)
        self.body = None

    @swagger_auto_schema(value='/api/user/register', method='post', operation_summary='注册接口', request_body=request_body, responses={0: access_response_schema, 201: 'None'})
    @csrf_exempt
    @api_view(['POST'])
    def register(request):
        data = json.loads(request.body.decode('utf-8'))
        phone = data['phone']
        password = data['password']
        if phone is None or password is None or password == '' or phone == '':
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
                        data.token = jwt.encode({'id': str(data.id), 'password': password + str(time.time())}, read_yaml('token_private_key', 'config.yaml'), algorithm='HS256')
                        data.save()
                        logging.info('注册成功')
                        Response = {
                            "code": 0,
                            "message": "注册成功",
                            "data": {
                                "id": data.id,
                                "username": data.username,
                                "phone": str(data.phone.replace(phone[3:7], '****')),
                                "token": str(data.token)
                            }
                        }
        return JsonResponse(Response)

    @swagger_auto_schema(value='/api/user/login',method='post', operation_summary='登录接口', request_body=request_body, responses={0: access_response_schema, 201: 'None'})
    @csrf_exempt
    @api_view(['POST'])
    def login(request):
        data = json.loads(request.body.decode('utf-8'))
        phone = data['phone']
        password = data['password']
        if phone is None or password is None or password == '' or phone == '':
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
                    data.token = jwt.encode({'id': str(data.id), 'password': password + str(time.time())}, read_yaml('token_private_key', 'config.yaml'), algorithm='HS256')
                    data.save()
                    logging.info('登录成功')
                    Response = {
                        "code": 0,
                        "message": "登录成功",
                        "data": {
                            "id": data.id,
                            "username": data.username,
                            "phone": str(data.phone.replace(phone[3:7], '****')),
                            "token": str(data.token)
                        }
                    }
        return JsonResponse(Response)
