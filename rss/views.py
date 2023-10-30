from rest_framework.views import APIView
from rest_framework.decorators import api_view
from django.views.decorators.csrf import csrf_exempt
from drf_yasg2 import openapi
from drf_yasg2.utils import swagger_auto_schema
from django.core.paginator import Paginator
import json, logging, requests
from django.http import JsonResponse
from .models import Rss
from push.models import Push
from django.forms import model_to_dict
from user.auth2 import JWTAuthentication
from rsspush.error_response import error_response


class RssView(APIView):
    authentication_classes = [JWTAuthentication, ]
    rss_list_query_param = [
        openapi.Parameter('page', openapi.IN_QUERY, type=openapi.TYPE_INTEGER, description="页数", default=1),
        openapi.Parameter('pageSize', openapi.IN_QUERY, type=openapi.TYPE_INTEGER, description="每页显示的条数", default=20),
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
        self.user = None
        self.POST = None
        self.body = None
        self.GET = None
        self.META = None

    @swagger_auto_schema(value='/api/rss/list', method='get', operation_summary='rss列表接口', manual_parameters=rss_list_query_param, responses={0: rss_list_access_response_schema, 201: 'None'})
    @csrf_exempt
    @api_view(['GET'])
    def rss_list(self):
        page = self.GET.get('page')
        pageSize = self.GET.get('pageSize')
        if pageSize == '' or page == '':
            logging.error(error_response.missing_parameter.value['message'])
            return JsonResponse(error_response.missing_parameter.value)
        page = int(page)
        pageSize = int(pageSize)
        if page is None:
            page = 1
        if pageSize is None or pageSize > 100:
            pageSize = 20
        rss = Rss.objects.filter(user_id=self.user.id).order_by('id')
        paginator = Paginator(rss, pageSize)
        page_obj = paginator.get_page(page)
        data_list = []
        for i in page_obj:
            mode_to = model_to_dict(i)  # exclude这个是转字典的时候去掉，哪个字段，就是不给哪个字段转成字典
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
        required=['rss_uri'],
        properties={
            'rss_uri': openapi.Schema(type=openapi.TYPE_STRING, description='rss的uri'),
        })

    add_rss_access_response_schema = openapi.Response(
        description='Successful response',
        schema=openapi.Schema(type=openapi.TYPE_OBJECT, properties={
            'code': openapi.Schema(type=openapi.TYPE_INTEGER, description='code'),
            'message': openapi.Schema(type=openapi.TYPE_STRING, description='message'),
        })
    )

    @swagger_auto_schema(value='/api/rss/add', method='post', operation_summary='添加rss接口', request_body=add_rss_request_body, responses={0: add_rss_access_response_schema, 201: 'None'})
    @csrf_exempt
    @api_view(['POST'])
    def add_rss(self):
        data = json.loads(self.body.decode('utf-8'))
        if data.get('rss_uri') is None:
            logging.error(error_response.missing_parameter.value['message'])
            return JsonResponse(error_response.missing_parameter.value)
        else:
            rss_uri = data['rss_uri']
            if rss_uri == '':
                logging.error(error_response.missing_parameter.value['message'])
                return JsonResponse(error_response.missing_parameter.value)
            else:
                if Rss.objects.create(user_id=self.user.id, rss_uri=rss_uri):
                    logging.info('用户' + str(self.user.id) + '已新增rss')
                    Response = {
                        "code": 0,
                        "message": "新增成功"
                    }
                    requests.get(url='http://127.0.0.1:8000/api/push/refresh')
                else:
                    logging.error(error_response.add_rss_error.value['message'])
                    return JsonResponse(error_response.add_rss_error.value)
        return JsonResponse(Response)

    edit_rss_request_body = openapi.Schema(
        type=openapi.TYPE_OBJECT,
        required=['id', 'rss_uri'],
        properties={
            'id': openapi.Schema(type=openapi.TYPE_INTEGER, description='id'),
            'rss_uri': openapi.Schema(type=openapi.TYPE_STRING, description='rss的uri'),
        })

    edit_rss_access_response_schema = openapi.Response(
        description='Successful response',
        schema=openapi.Schema(type=openapi.TYPE_OBJECT, properties={
            'code': openapi.Schema(type=openapi.TYPE_INTEGER, description='code'),
            'message': openapi.Schema(type=openapi.TYPE_STRING, description='message'),
        })
    )

    @swagger_auto_schema(value='/api/rss/edit', method='Put', operation_summary='编辑rss接口', request_body=edit_rss_request_body, responses={0: edit_rss_access_response_schema, 201: 'None'})
    @csrf_exempt
    @api_view(['PUT'])
    def edit_rss(self):
        data = json.loads(self.body.decode('utf-8'))
        if data.get('rss_uri') is None or data.get('id') is None:
            logging.error(error_response.missing_parameter.value['message'])
            return JsonResponse(error_response.missing_parameter.value)
        else:
            rss_uri = data['rss_uri']
            id = data['id']
            if id == '' or rss_uri == '':
                logging.error(error_response.missing_parameter.value['message'])
                return JsonResponse(error_response.missing_parameter.value)
            else:
                if not Rss.objects.filter(id=id).count():
                    logging.error(error_response.no_data.value['message'])
                    return JsonResponse(error_response.no_data.value)
                else:
                    data = Rss.objects.get(id=id)
                    data.rss_uri = rss_uri
                    data.save()
                    logging.error('修改成功')
                    Response = {
                        "code": 0,
                        "message": "修改成功"
                    }
                    requests.get(url='http://127.0.0.1:8000/api/push/refresh')
        return JsonResponse(Response)

    delete_rss_request_body = openapi.Schema(
        type=openapi.TYPE_OBJECT,
        required=['id'],
        properties={
            'id': openapi.Schema(type=openapi.TYPE_INTEGER, description='id'),
        })

    delete_rss_access_response_schema = openapi.Response(
        description='Successful response',
        schema=openapi.Schema(type=openapi.TYPE_OBJECT, properties={
            'code': openapi.Schema(type=openapi.TYPE_INTEGER, description='code'),
            'message': openapi.Schema(type=openapi.TYPE_STRING, description='message'),
        })
    )

    @swagger_auto_schema(value='/api/rss/delete', method='delete', operation_summary='删除rss接口', request_body=delete_rss_request_body, responses={0: delete_rss_access_response_schema, 201: 'None'})
    @csrf_exempt
    @api_view(['DELETE'])
    def delete_rss(self):
        data = json.loads(self.body.decode('utf-8'))
        if data.get('id') is None:
            logging.error(error_response.missing_parameter.value['message'])
            return JsonResponse(error_response.missing_parameter.value)
        else:
            id = data['id']
            if id is None or id == '':
                logging.error(error_response.missing_parameter.value['message'])
                return JsonResponse(error_response.missing_parameter.value)
            else:
                push_id = Rss.objects.get(id=id).push_id
                if push_id is not None:
                    Push.objects.get(id=push_id).delete()
                    logging.info('用户' + str(self.user.id) + '已删除push' + str(push_id))
                if Rss.objects.get(id=id).delete():
                    logging.info('用户' + str(self.user.id) + '已删除rss' + str(id))
                    Response = {
                        "code": 0,
                        "message": "删除成功"
                    }
                    requests.get(url='http://127.0.0.1:8000/api/push/refresh')
                else:
                    logging.error(error_response.delete_error.value['message'])
                    return JsonResponse(error_response.delete_error.value)
        return JsonResponse(Response)

