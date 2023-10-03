from rest_framework.views import APIView
from rest_framework.decorators import api_view
from django.views.decorators.csrf import csrf_exempt
from rest_framework import serializers, views, response
from django.core.paginator import Paginator
import json, logging
from django.http import JsonResponse
from .models import Rss
from user.models import User



class RssView(APIView):

    @csrf_exempt
    @api_view(['POST'])
    def addRss(request):
        pass

    @csrf_exempt
    @api_view(['POST'])
    def delRss(request):
        pass

    @csrf_exempt
    @api_view(['GET'])
    def listRss(request):
        page = request.GET.get('page', 1)
        pageSize = request.GET.get('pageSize', 20)
        token = request.headers['token']
        if token is None or not User.objects.filter(token=token).count():
            logging.error('您还未登录')
            Response = {
                "code": 10006,
                "message": "您还未登录"
            }
        rss = Rss.objects.filter(user_id=User.objects.get(token=token).id)
        paginator = Paginator(rss, pageSize)
        page_obj = paginator.get_page(page)
        # data = serializer.data
        Response = {
            "code": 0,
            "message": "获取成功",
            "data": page_obj
        }



        return JsonResponse(Response)
