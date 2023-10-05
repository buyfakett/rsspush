from rest_framework.views import APIView
from rest_framework.decorators import api_view
from django.views.decorators.csrf import csrf_exempt
from rest_framework import serializers, views, response
from drf_yasg2 import openapi
from drf_yasg2.utils import swagger_auto_schema
from django.core.paginator import Paginator
import json, logging
from django.http import JsonResponse
from .models import Rss
from user.models import User


class RssView(APIView):
    query_param = [
        openapi.Parameter('page', openapi.IN_QUERY, type=openapi.TYPE_INTEGER, description="页数"),
        openapi.Parameter('pageSize', openapi.IN_QUERY, type=openapi.TYPE_INTEGER, description="每页显示的条数"),
    ]

    access_response_schema = openapi.Response(
        description='Successful response',
        schema=openapi.Schema(type=openapi.TYPE_OBJECT, properties={
            'code': openapi.Schema(type=openapi.TYPE_INTEGER, description='code'),
            'message': openapi.Schema(type=openapi.TYPE_STRING, description='message'),
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
        self.META = None

    @swagger_auto_schema(value='/api/rss/list', method='get', operation_summary='rss列表接口', manual_parameters=query_param, responses={0: access_response_schema, 201: 'None'})
    @csrf_exempt
    @api_view(['GET'])
    def listRss(request):
        token = request.META.get('HTTP_AUTHORIZATION')
        page = request.META.get('page', 1)
        pageSize = request.META.get('pageSize', 20)
        if token is None or not User.objects.filter(token=token).count():
            logging.error('您还未登录')
            Response = {
                "code": 10006,
                "message": "您还未登录"
            }
        else:
            rss = Rss.objects.filter(user_id=User.objects.get(token=token).id)
            paginator = Paginator(rss, pageSize)
            page_obj = paginator.get_page(page)
            Response = {
                "code": 0,
                "message": "获取成功",
                "data": page_obj
            }



        return JsonResponse(Response)

    @swagger_auto_schema(value='/api/rss/add', method='post', operation_summary='添加rss接口', responses={201: 'None'})
    @csrf_exempt
    @api_view(['POST'])
    def addRss(request):
        pass

    @swagger_auto_schema(value='/api/rss/del', method='post', operation_summary='删除rss接口', responses={201: 'None'})
    @csrf_exempt
    @api_view(['POST'])
    def delRss(request):
        pass

