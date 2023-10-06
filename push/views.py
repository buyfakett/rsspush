from rest_framework.views import APIView
from rest_framework.decorators import api_view
from django.views.decorators.csrf import csrf_exempt
from drf_yasg2.utils import swagger_auto_schema
from drf_yasg2 import openapi
import json, logging
from django.http import JsonResponse
from .models import Push
from user.models import User
from rss.models import Rss
from util.token_util import check_token


class RssView(APIView):
    def __init__(self, **kwargs):
        super().__init__(kwargs)
        self.GET = None
        self.META = None
        self.body = None

    add_push_request_body = openapi.Schema(
        type=openapi.TYPE_OBJECT,
        required=['user_id', 'push_type', 'rss_id', 'ding_access_token', 'ding_keyword', 'wechat_template_id', 'wechat_app_id', 'wechat_to_user_ids'],
        properties={
            'user_id': openapi.Schema(type=openapi.TYPE_INTEGER, description='用户id'),
            'rss_id': openapi.Schema(type=openapi.TYPE_INTEGER, description='rss表的id'),
            'push_type': openapi.Schema(type=openapi.TYPE_STRING, description='钉钉推送还是微信测试号推送(钉钉：ding，微信测试号：wechat)"'),
            'ding_access_token': openapi.Schema(type=openapi.TYPE_STRING, description='钉钉参数'),
            'ding_keyword': openapi.Schema(type=openapi.TYPE_STRING, description='钉钉自定义关键词'),
            'wechat_template_id': openapi.Schema(type=openapi.TYPE_STRING, description='微信模板id'),
            'wechat_app_id': openapi.Schema(type=openapi.TYPE_STRING, description='微信appId'),
            'wechat_to_user_ids': openapi.Schema(type=openapi.TYPE_STRING, description='微信发送的用户们'),
        })

    base_access_response_schema = openapi.Response(
        description='Successful response',
        schema=openapi.Schema(type=openapi.TYPE_OBJECT, properties={
            'code': openapi.Schema(type=openapi.TYPE_INTEGER, description='code'),
            'message': openapi.Schema(type=openapi.TYPE_STRING, description='message'),
        })
    )

    @swagger_auto_schema(value='/api/push/add', method='post', operation_summary='新增推送接口', request_body=add_push_request_body, responses={0: base_access_response_schema, 201: 'None'})
    @csrf_exempt
    @api_view(['POST'])
    def add_push(self):
        token = self.META.get('HTTP_AUTHORIZATION')
        data = json.loads(self.body.decode('utf-8'))
        if data.get('user_id') is None or data.get('push_type') is None or data.get('rss_id') is None:
            logging.error('参数缺少')
            Response = {
                "code": 10010,
                "message": "参数缺少"
            }
        else:
            user_id = data['user_id']
            rss_id = data['rss_id']
            push_type = data['push_type']
            Response = json.loads(check_token(token))
            if Response['code'] == 0:
                if not User.objects.get(id=user_id).token == token:
                    logging.error('别用别人的token')
                    Response = {
                        "code": 10008,
                        "message": "别用别人的token"
                    }
                else:
                    rss_push_id = Rss.objects.get(id=rss_id).push_id
                    if not rss_push_id is None or rss_push_id == '':
                        logging.error('此rss已有push数据，应该调修改接口')
                        Response = {
                            "code": 10013,
                            "message": "此rss已有push数据，应该调修改接口"
                        }
                    else:
                        if push_type == 'ding':
                            if data.get('ding_access_token') is None or data.get('ding_keyword') is None:
                                logging.error('参数缺少')
                                Response = {
                                    "code": 10010,
                                    "message": "参数缺少"
                                }
                            else:
                                ding_access_token = data['ding_access_token']
                                ding_keyword = data['ding_keyword']
                                create_push = Push.objects.create(push_type=push_type, ding_access_token=ding_access_token, ding_keyword=ding_keyword)
                                data = Rss.objects.get(id=rss_id)
                                data.push_id = create_push.id
                                data.save()
                                logging.info('用户' + str(user_id) + '已新增push')
                                Response = {
                                    "code": 0,
                                    "message": "新增成功"
                                }
                        elif push_type == 'wechat':
                            if data.get('wechat_template_id') is None or data.get('wechat_app_id') is None or data.get('wechat_to_user_ids') is None:
                                logging.error('参数缺少')
                                Response = {
                                    "code": 10010,
                                    "message": "参数缺少"
                                }
                            else:
                                wechat_template_id = data['wechat_template_id']
                                wechat_app_id = data['wechat_app_id']
                                wechat_to_user_ids = data['wechat_to_user_ids']
                                create_push = Push.objects.create(push_type=push_type, wechat_template_id=wechat_template_id, wechat_app_id=wechat_app_id, wechat_to_user_ids=wechat_to_user_ids)
                                data = Rss.objects.get(id=rss_id)
                                data.push_id = create_push.id
                                data.save()
                                logging.info('用户' + str(user_id) + '已新增push')
                                Response = {
                                    "code": 0,
                                    "message": "新增成功"
                                }
                        else:
                            logging.error('没有这个推送选项')
                            Response = {
                                "code": 10012,
                                "message": "没有这个推送选项"
                            }
        return JsonResponse(Response)

    edit_push_request_body = openapi.Schema(
        type=openapi.TYPE_OBJECT,
        required=['id', 'user_id', 'push_type', 'ding_access_token', 'ding_keyword', 'wechat_template_id', 'wechat_app_id', 'wechat_to_user_ids'],
        properties={
            'id': openapi.Schema(type=openapi.TYPE_INTEGER, description='id'),
            'user_id': openapi.Schema(type=openapi.TYPE_INTEGER, description='用户id'),
            'push_type': openapi.Schema(type=openapi.TYPE_STRING, description='钉钉推送还是微信测试号推送(钉钉：ding，微信测试号：wechat)"'),
            'ding_access_token': openapi.Schema(type=openapi.TYPE_STRING, description='钉钉参数'),
            'ding_keyword': openapi.Schema(type=openapi.TYPE_STRING, description='钉钉自定义关键词'),
            'wechat_template_id': openapi.Schema(type=openapi.TYPE_STRING, description='微信模板id'),
            'wechat_app_id': openapi.Schema(type=openapi.TYPE_STRING, description='微信appId'),
            'wechat_to_user_ids': openapi.Schema(type=openapi.TYPE_STRING, description='微信发送的用户们'),
        })

    @swagger_auto_schema(value='/api/push/edit', method='post', operation_summary='编辑推送接口', request_body=edit_push_request_body, responses={0: base_access_response_schema, 201: 'None'})
    @csrf_exempt
    @api_view(['POST'])
    def edit_push(self):
        token = self.META.get('HTTP_AUTHORIZATION')
        data = json.loads(self.body.decode('utf-8'))
        if data.get('user_id') is None or data.get('push_type') is None or data.get('id') is None:
            logging.error('参数缺少')
            Response = {
                "code": 10010,
                "message": "参数缺少"
            }
        else:
            user_id = data['user_id']
            id = data['id']
            push_type = data['push_type']
            Response = json.loads(check_token(token))
            if Response['code'] == 0:
                if not User.objects.get(id=user_id).token == token:
                    logging.error('别用别人的token')
                    Response = {
                        "code": 10008,
                        "message": "别用别人的token"
                    }
                else:
                    if push_type == 'ding':
                        if data.get('ding_access_token') is None or data.get('ding_keyword') is None:
                            logging.error('参数缺少')
                            Response = {
                                "code": 10010,
                                "message": "参数缺少"
                            }
                        else:
                            ding_access_token = data['ding_access_token']
                            ding_keyword = data['ding_keyword']
                            data = Push.objects.get(id=id)
                            data.ding_keyword = ding_keyword
                            data.ding_access_token = ding_access_token
                            data.save()
                            logging.info('用户' + str(user_id) + '已修改push' + str(id))
                            Response = {
                                "code": 0,
                                "message": "修改成功"
                            }
                    elif push_type == 'wechat':
                        if data.get('wechat_template_id') is None or data.get('wechat_app_id') is None or data.get('wechat_to_user_ids') is None:
                            logging.error('参数缺少')
                            Response = {
                                "code": 10010,
                                "message": "参数缺少"
                            }
                        else:
                            wechat_template_id = data['wechat_template_id']
                            wechat_app_id = data['wechat_app_id']
                            wechat_to_user_ids = data['wechat_to_user_ids']
                            data = Push.objects.get(id=id)
                            data.wechat_template_id = wechat_template_id
                            data.wechat_app_id = wechat_app_id
                            data.wechat_to_user_ids = wechat_to_user_ids
                            data.save()
                            logging.info('用户' + str(user_id) + '已修改push' + str(id))
                            Response = {
                                "code": 0,
                                "message": "修改成功"
                            }
                    else:
                        logging.error('没有这个推送选项')
                        Response = {
                            "code": 10012,
                            "message": "没有这个推送选项"
                        }
        return JsonResponse(Response)

    delete_push_request_body = openapi.Schema(
        type=openapi.TYPE_OBJECT,
        required=['user_id', 'push_type'],
        properties={
            'user_id': openapi.Schema(type=openapi.TYPE_INTEGER, description='用户id'),
            'rss_id': openapi.Schema(type=openapi.TYPE_INTEGER, description='rss表的id'),
        })

    @swagger_auto_schema(value='/api/push/del', method='delete', operation_summary='删除推送接口', request_body=delete_push_request_body, responses={0: base_access_response_schema, 201: 'None'})
    @csrf_exempt
    @api_view(['DELETE'])
    def delete_push(self):
        token = self.META.get('HTTP_AUTHORIZATION')
        data = json.loads(self.body.decode('utf-8'))
        if data.get('user_id') is None or data.get('rss_id') is None:
            logging.error('参数缺少')
            Response = {
                "code": 10010,
                "message": "参数缺少"
            }
        else:
            user_id = data['user_id']
            rss_id = data['rss_id']
            Response = json.loads(check_token(token))
            if Response['code'] == 0:
                if not User.objects.get(id=user_id).token == token:
                    logging.error('别用别人的token')
                    Response = {
                        "code": 10008,
                        "message": "别用别人的token"
                    }
                else:
                    if Push.objects.get(id=rss_id).delete():
                        data = Rss.objects.get(id=rss_id)
                        data.push_id = ''
                        data.save()
                        logging.info('用户' + str(user_id) + '已删除push' + str(rss_id))
                        Response = {
                            "code": 0,
                            "message": "删除成功"
                        }
                    else:
                        logging.error('删除失败')
                        Response = {
                            "code": 10009,
                            "message": "删除失败"
                        }
        return JsonResponse(Response)

    push_view_query_param = [
        openapi.Parameter('user_id', openapi.IN_QUERY, type=openapi.TYPE_INTEGER, description="user_id"),
        openapi.Parameter('rss_id', openapi.IN_QUERY, type=openapi.TYPE_INTEGER, description="rss表的id"),
    ]

    push_view_access_response_schema = openapi.Response(
        description='Successful response',
        schema=openapi.Schema(type=openapi.TYPE_OBJECT, properties={
            'code': openapi.Schema(type=openapi.TYPE_INTEGER, description='code'),
            'message': openapi.Schema(type=openapi.TYPE_STRING, description='message'),
            'data': openapi.Schema(type=openapi.TYPE_OBJECT, description='data', properties={
                'push_type': openapi.Schema(type=openapi.TYPE_STRING, description='钉钉推送还是微信测试号推送(钉钉：ding，微信测试号：wechat)"'),
                'ding_access_token': openapi.Schema(type=openapi.TYPE_STRING, description='钉钉参数'),
                'ding_keyword': openapi.Schema(type=openapi.TYPE_STRING, description='钉钉自定义关键词'),
                'wechat_template_id': openapi.Schema(type=openapi.TYPE_STRING, description='微信模板id'),
                'wechat_app_id': openapi.Schema(type=openapi.TYPE_STRING, description='微信appId'),
                'wechat_to_user_ids': openapi.Schema(type=openapi.TYPE_STRING, description='微信发送的用户们'),
            }),
        })
    )

    @swagger_auto_schema(value='/api/push/view', method='get', operation_summary='查看push接口', manual_parameters=push_view_query_param, responses={0: push_view_access_response_schema, 201: 'None'})
    @csrf_exempt
    @api_view(['GET'])
    def view(self):
        data = {
            "push_type": "",
            "ding_access_token": "",
            "ding_keyword": "",
            "wechat_template_id": "",
            "wechat_app_id": "",
            "wechat_to_user_ids": "",
        }
        token = self.META.get('HTTP_AUTHORIZATION')
        user_id = self.GET.get('user_id')
        rss_id = self.GET.get('rss_id')
        if user_id is None or user_id == '' or rss_id is None or rss_id == '':
            logging.error('参数缺少')
            Response = {
                "code": 10010,
                "message": "参数缺少"
            }
        else:
            Response = json.loads(check_token(token))
            if Response['code'] == 0:
                if not User.objects.get(id=user_id).token == token:
                    logging.error('别用别人的token')
                    Response = {
                        "code": 10008,
                        "message": "别用别人的token"
                    }
                else:
                    rss_push_id = Rss.objects.get(id=rss_id).push_id
                    if rss_push_id is None or rss_push_id == '':
                        logging.info('用户' + str(user_id) + 'push' + str(rss_push_id) + '无推送配置')
                        Response = {
                            "code": 0,
                            "message": "无推送配置",
                            "data": data
                        }
                    else:
                        push_data = Push.objects.get(id=rss_push_id)
                        data['push_type'] = push_data.push_type
                        data['ding_access_token'] = push_data.ding_access_token
                        data['ding_keyword'] = push_data.ding_keyword
                        data['wechat_template_id'] = push_data.wechat_template_id
                        data['wechat_to_user_ids'] = push_data.wechat_to_user_ids
                        logging.info('用户' + str(user_id) + 'push' + str(rss_push_id) + '获取成功')
                        Response = {
                            "code": 0,
                            "message": "获取成功",
                            "data": data
                        }
        return JsonResponse(Response)