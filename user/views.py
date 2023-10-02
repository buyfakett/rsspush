from django.http import JsonResponse
from rest_framework.decorators import api_view
from django.views.decorators.csrf import csrf_exempt
from .models import User
import re, logging, hashlib
from drf_yasg2 import openapi
from drf_yasg2.utils import swagger_auto_schema
from rest_framework.views import APIView
import json, jwt, time

logging.basicConfig(level=logging.DEBUG)


class UserView(APIView):
    request_body = openapi.Schema(
        type=openapi.TYPE_OBJECT,
        required=['phone', 'password'],
        properties={
            'phone': openapi.Schema(type=openapi.TYPE_STRING, description='手机号'),
            'password': openapi.Schema(type=openapi.TYPE_STRING, description='密码')
        })
    response_schema = openapi.Response(
        description='Successful response',
        schema=openapi.Schema(type=openapi.TYPE_OBJECT, properties={
            'code': openapi.Schema(type=openapi.TYPE_INTEGER, description='code'),
            'message': openapi.Schema(type=openapi.TYPE_STRING, description='message'),
        })
    )

    @swagger_auto_schema(value='/api/user/login', method='post', operation_summary='注册接口', request_body=request_body, responses={0: response_schema})
    @csrf_exempt
    @api_view(['POST'])
    def register(request):
        data = json.loads(request.body.decode('utf-8'))
        phone = data['phone']
        password = data['password']
        if phone is None or password is None:
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
                        Response = {
                            "code": 0,
                            "message": "注册成功"
                        }
        return JsonResponse(Response)

    request_body = openapi.Schema(
        type=openapi.TYPE_OBJECT,
        required=['phone', 'password'],
        properties={
            'phone': openapi.Schema(type=openapi.TYPE_STRING, description='手机号'),
            'password': openapi.Schema(type=openapi.TYPE_STRING, description='密码')
        })
    login_response_schema = openapi.Response(
        description='Successful response',
        schema=openapi.Schema(type=openapi.TYPE_OBJECT, properties={
            'code': openapi.Schema(type=openapi.TYPE_INTEGER, description='code'),
            'data': openapi.Schema(type=openapi.TYPE_OBJECT, description='data', properties={
                'username': openapi.Schema(type=openapi.TYPE_INTEGER, description='username'),
                'phone': openapi.Schema(type=openapi.TYPE_INTEGER, description='phone'),
                'token': openapi.Schema(type=openapi.TYPE_INTEGER, description='token'),
            }),
        })
    )

    @swagger_auto_schema(value='/api/user/login', method='post', operation_summary='登录接口', request_body=request_body, responses={0: login_response_schema})
    @csrf_exempt
    @api_view(['POST'])
    def login(request):
        data = json.loads(request.body.decode('utf-8'))
        phone = data['phone']
        password = data['password']
        if phone is None or password is None:
            logging.error('请输入手机号和密码')
            Response = {
                "code": 10003,
                "message": "请输入手机号和密码"
            }
        else:
            if not (User.objects.filter(phone=phone)).count():
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
                    Response = {
                        "code": 10006,
                        "message": "密码错误"
                    }
                else:
                    data.token = jwt.encode({'username': data.username, 'password': password + str(time.time())}, 'rsspush', algorithm='HS256')
                    data.save()
                    Response = {
                        "code": 0,
                        "data": {
                            "username": data.username,
                            "phone": data.phone,
                            "token": data.token
                        }
                    }
        return JsonResponse(Response)
