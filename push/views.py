from rest_framework.views import APIView
from rest_framework.decorators import api_view
from django.views.decorators.csrf import csrf_exempt
from drf_yasg2.utils import swagger_auto_schema
from drf_yasg2 import openapi


class RssView(APIView):
    add_push_request_body = openapi.Schema(
        type=openapi.TYPE_OBJECT,
        required=['user_id', 'push_type', 'ding_access_token', 'ding_keyword', 'wechat_template_id', 'wechat_app_id', 'wechat_to_user_ids'],
        properties={
            'user_id': openapi.Schema(type=openapi.TYPE_INTEGER, description='用户id'),
            'push_type': openapi.Schema(type=openapi.TYPE_STRING, description='钉钉推送还是微信测试号推送(钉钉：ding，微信测试号：wechat)"'),
            'ding_access_token': openapi.Schema(type=openapi.TYPE_STRING, description='钉钉参数'),
            'ding_keyword': openapi.Schema(type=openapi.TYPE_STRING, description='钉钉自定义关键词'),
            'wechat_template_id': openapi.Schema(type=openapi.TYPE_STRING, description='微信模板id'),
            'wechat_app_id': openapi.Schema(type=openapi.TYPE_STRING, description='微信appId'),
            'wechat_to_user_ids': openapi.Schema(type=openapi.TYPE_STRING, description='微信发送的用户们'),
        })

    add_push_access_response_schema = openapi.Response(
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

    @swagger_auto_schema(value='/api/push/add', method='post', operation_summary='新增推送接口', request_body=add_push_request_body, responses={0: add_push_access_response_schema, 201: 'None'})
    @csrf_exempt
    @api_view(['POST'])
    def add_push(self):
        pass

    @swagger_auto_schema(value='/api/push/edit', method='post', operation_summary='编辑推送接口', responses={201: 'None'})
    @csrf_exempt
    @api_view(['POST'])
    def edit_push(self):
        pass

    @swagger_auto_schema(value='/api/push/del', method='delete', operation_summary='删除推送接口', responses={201: 'None'})
    @csrf_exempt
    @api_view(['DELETE'])
    def delete_push(self):
        pass

    @swagger_auto_schema(value='/api/push/view', method='get', operation_summary='push列表接口', responses={201: 'None'})
    @csrf_exempt
    @api_view(['GET'])
    def view(self):
        pass