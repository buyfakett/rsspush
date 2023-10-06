from rest_framework.views import APIView
from rest_framework.decorators import api_view
from django.views.decorators.csrf import csrf_exempt
from rest_framework import serializers, views, response
from drf_yasg2 import openapi
from drf_yasg2.utils import swagger_auto_schema
from django.core.paginator import Paginator
import json, logging, re
from django.http import JsonResponse
from .models import Rss
from user.models import User
from django.forms import model_to_dict
from util.token_util import check_token


class RssView(APIView):
    rss_list_query_param = [
        openapi.Parameter('page', openapi.IN_QUERY, type=openapi.TYPE_INTEGER, description="页数"),
        openapi.Parameter('pageSize', openapi.IN_QUERY, type=openapi.TYPE_INTEGER, description="每页显示的条数"),
    ]

    rss_list_access_response_schema = openapi.Response(
        description='Successful response',
        schema=openapi.Schema(type=openapi.TYPE_OBJECT, properties={
            'code': openapi.Schema(type=openapi.TYPE_INTEGER, description='code'),
            'message': openapi.Schema(type=openapi.TYPE_STRING, description='message'),
            'page': openapi.Schema(type=openapi.TYPE_STRING, description='当前页数'),
            'count': openapi.Schema(type=openapi.TYPE_STRING, description='一共的数据'),
            'data': openapi.Schema(type=openapi.TYPE_OBJECT, description='data', properties={
                'push_id': openapi.Schema(type=openapi.TYPE_INTEGER, description='push_id'),
                'rss_uri': openapi.Schema(type=openapi.TYPE_STRING, description='rss的uri'),
                'detection_time': openapi.Schema(type=openapi.TYPE_STRING, description='检测的时间(分钟）'),
                'timestamp': openapi.Schema(type=openapi.TYPE_STRING, description='上次更新的时间戳'),
            }),
        })
    )

    def __init__(self, **kwargs):
        super().__init__(kwargs)
        self.body = None
        self.GET = None
        self.META = None

    @swagger_auto_schema(value='/api/rss/list', method='get', operation_summary='rss列表接口', manual_parameters=rss_list_query_param, responses={0: rss_list_access_response_schema, 201: 'None'})
    @csrf_exempt
    @api_view(['GET'])
    def rss_list(self):
        token = self.META.get('HTTP_AUTHORIZATION')
        page = self.GET.get('page', 1)
        pageSize = self.GET.get('pageSize', 20)
        if page == '':
            page = 1
        if pageSize == '':
            pageSize = 20
        Response = json.loads(check_token(token))
        if Response['code'] == 0:
            rss = Rss.objects.filter(user_id=User.objects.get(token=token).id)
            paginator = Paginator(rss, pageSize)
            page_obj = paginator.get_page(page)
            data_list = []
            for i in page_obj:
                mode_to = model_to_dict(i, exclude='user_id')  # exclude这个是转字典的时候去掉，哪个字段，就是不给哪个字段转成字典
                data_list.append(mode_to)
            Response = {
                "code": 0,
                "message": "获取成功",
                "page": page,
                "count": paginator.count,
                "data": data_list
            }

        return JsonResponse(Response)

    add_rss_request_body = openapi.Schema(
        type=openapi.TYPE_OBJECT,
        required=['phone', 'password'],
        properties={
            'user_id': openapi.Schema(type=openapi.TYPE_STRING, description='用户id'),
            'push_id': openapi.Schema(type=openapi.TYPE_STRING, description='推送表的id'),
            'rss_uri': openapi.Schema(type=openapi.TYPE_STRING, description='密码'),
            'detection_time': openapi.Schema(type=openapi.TYPE_STRING, description='密码'),
            'timestamp': openapi.Schema(type=openapi.TYPE_STRING, description='密码'),
        })

    add_rss_access_response_schema = openapi.Response(
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

    @swagger_auto_schema(value='/api/rss/add', method='post', operation_summary='添加rss接口', request_body=add_rss_request_body, responses={0: add_rss_access_response_schema, 201: 'None'})
    @csrf_exempt
    @api_view(['POST'])
    def add_rss(self):
        data = json.loads(self.body.decode('utf-8'))
        token = self.META.get('HTTP_AUTHORIZATION')

    @swagger_auto_schema(value='/api/rss/del', method='post', operation_summary='删除rss接口', responses={201: 'None'})
    @csrf_exempt
    @api_view(['POST'])
    def delete_rss(self):
        pass

