from django.http import JsonResponse
from rest_framework.decorators import api_view
from django.views.decorators.csrf import csrf_exempt
from .models import User
from drf_yasg2 import openapi
from drf_yasg2.utils import swagger_auto_schema
from rest_framework.views import APIView
import json, re, logging, hashlib
from user.auth import create_token
from user.auth2 import JWTAuthentication
from rsspush.error_response import error_response
from rsspush.success_response import success_response


class UserView(APIView):
    authentication_classes = [JWTAuthentication, ]
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
        self.user = None
        self.META = None
        self.body = None

    @swagger_auto_schema(value='/api/user/register', method='post', operation_summary='注册接口', request_body=request_body, responses={0: access_response_schema, 201: 'None'})
    @csrf_exempt
    @api_view(['POST'])
    def register(self):
        data = json.loads(self.body.decode('utf-8'))
        if data.get('phone') is None or data.get('password') is None:
            logging.error(error_response.missing_parameter.value['message'])
            return JsonResponse(error_response.missing_parameter.value)
        else:
            phone = data['phone']
            password = data['password']
            if password == '' or phone == '':
                logging.error(error_response.missing_parameter.value['message'])
                return JsonResponse(error_response.missing_parameter.value)
            else:
                if not re.match('^(13|14|15|16|17|18)[0-9]{9}$', str(phone)):
                    logging.error(error_response.phone_error.value['message'])
                    return JsonResponse(error_response.phone_error.value)
                else:
                    if not re.match('^(?![0-9]+$)(?![a-zA-Z]+$)[0-9A-Za-z]{6,16}$', str(password)):
                        logging.error(error_response.password_format_error.value['message'])
                        return JsonResponse(error_response.password_format_error.value)
                    else:
                        if (User.objects.filter(phone=phone)).count():
                            logging.error(error_response.phone_repeat_error.value['message'])
                            return JsonResponse(error_response.phone_repeat_error.value)
                        else:
                            Encry = hashlib.md5()  # 实例化md5
                            Encry.update(password.encode('utf-8'))  # 字符串字节加密
                            password = Encry.hexdigest()  # 字符串加密
                            User.objects.create(phone=phone, username=phone, password=password)
                            data = User.objects.get(phone=phone)
                            data.token = create_token(user_id=User.objects.get(phone=phone).id)
                            data.save()
                            logging.info('注册成功')
                            Response_data = {
                                "user_id": data.id,
                                "username": data.username,
                                "phone": str(data.phone.replace(phone[3:7], '****')),
                                "token": str(data.token)
                            }
                            return success_response(0, "注册成功", Response_data)

    @swagger_auto_schema(value='/api/user/login',method='post', operation_summary='登录接口', request_body=request_body, responses={0: access_response_schema, 201: 'None'})
    @csrf_exempt
    @api_view(['POST'])
    def login(self):
        data = json.loads(self.body.decode('utf-8'))
        if data.get('phone') is None or data.get('password') is None:
            logging.error(error_response.missing_parameter.value['message'])
            return JsonResponse(error_response.missing_parameter.value)
        else:
            phone = data['phone']
            password = data['password']
            if password == '' or phone == '':
                logging.error(error_response.missing_parameter.value['message'])
                return JsonResponse(error_response.missing_parameter.value)
            else:
                if not (User.objects.filter(phone=phone)).count():
                    logging.error(error_response.phone_not_found_error.value['message'])
                    return JsonResponse(error_response.phone_not_found_error.value)
                else:
                    Encry = hashlib.md5()  # 实例化md5
                    Encry.update(password.encode('utf-8'))  # 字符串字节加密
                    password = Encry.hexdigest()  # 字符串加密
                    data = User.objects.get(phone=phone)
                    if data.password != password:
                        logging.error(error_response.password_error.value['message'])
                        return JsonResponse(error_response.password_error.value)
                    else:
                        data.token = create_token(user_id=data.id)
                        data.save()
                        logging.info('登录成功')
                        Response_data = {
                                "user_id": data.id,
                                "username": data.username,
                                "phone": str(data.phone.replace(phone[3:7], '****')),
                                "token": str(data.token)
                            }
                        return success_response(0, "登录成功", Response_data)

    change_password_request_body = openapi.Schema(
        type=openapi.TYPE_OBJECT,
        required=['old_password', 'password'],
        properties={
            'old_password': openapi.Schema(type=openapi.TYPE_STRING, description='旧密码'),
            'password': openapi.Schema(type=openapi.TYPE_STRING, description='密码')
        })

    @swagger_auto_schema(value='/api/user/reset', method='put', operation_summary='修改密码接口', request_body=change_password_request_body, responses={0: access_response_schema, 201: 'None'})
    @csrf_exempt
    @api_view(['PUT'])
    def change_password(self):
        data = json.loads(self.body.decode('utf-8'))
        if data.get('old_password') is None or data.get('password') is None:
            logging.error(error_response.missing_parameter.value['message'])
            return JsonResponse(error_response.missing_parameter.value)
        else:
            old_password = data['old_password']
            password = data['password']
            if old_password == '' or password == '':
                logging.error(error_response.missing_parameter.value['message'])
                return JsonResponse(error_response.missing_parameter.value)
            else:
                if not re.match('^(?![0-9]+$)(?![a-zA-Z]+$)[0-9A-Za-z]{6,16}$', str(password)):
                    logging.error(error_response.password_format_error.value['message'])
                    return JsonResponse(error_response.password_format_error.value)
                else:
                    Encry_old_password = hashlib.md5()  # 实例化md5
                    Encry_old_password.update(old_password.encode('utf-8'))  # 字符串字节加密
                    old_password = Encry_old_password.hexdigest()  # 字符串加密
                    Encry_password = hashlib.md5()  # 实例化md5
                    Encry_password.update(password.encode('utf-8'))  # 字符串字节加密
                    password = Encry_password.hexdigest()  # 字符串加密
                    if self.user.password != old_password:
                        logging.error(error_response.old_password_error.value['message'])
                        return JsonResponse(error_response.old_password_error.value)
                    else:
                        self.user.password = password
                        self.user.token = create_token(user_id=self.user.id)
                        self.user.save()
                        logging.info('修改密码成功')
                        Response_data = {
                                "user_id": self.user.id,
                                "username": self.user.username,
                                "phone": str(self.user.phone.replace(self.user.phone[3:7], '****')),
                                "token": str(self.user.token)
                            }
                        return success_response(0, "修改密码成功", Response_data)
