from rest_framework.views import APIView
from rest_framework.decorators import api_view
from django.views.decorators.csrf import csrf_exempt
from drf_yasg2.utils import swagger_auto_schema
from drf_yasg2 import openapi
import json, logging, feedparser, datetime, requests, os, sys, random
from django.http import JsonResponse
from .models import Push
from rss.models import Rss
from user.auth2 import JWTAuthentication
from util.yaml_util import read_yaml
from rsspush.error_response import error_response
from rsspush.success_response import success_response
from datetime import datetime as dt
from django.conf import settings

TEST = False

def send_ding_message(access_token, keyword, now_time, title, link):
    test_data = {
        "msgtype": "link",
        "link": {
            "text": title,
            "title": keyword,
            "picUrl": "",
            "messageUrl": link
        }
    }
    test_url = "https://oapi.dingtalk.com/robot/send?access_token=" + access_token
    response = requests.post(test_url, json=test_data)
    if json.loads(response.text)['errcode'] == 0:
        logging.info(now_time + "推送钉钉：" + json.loads(response.text)['errmsg'])
    else:
        logging.error('推送错误')


def get_wechat_access_token(app_id, app_secret, now_time):
    # appId
    global access_token
    app_id = app_id
    # appSecret
    app_secret = app_secret
    post_url = ("https://api.weixin.qq.com/cgi-bin/token?grant_type=client_credential&appid={}&secret={}"
                .format(app_id, app_secret))
    try:
        access_token = requests.get(post_url).json()['access_token']
    except KeyError:
        logging.error(now_time + '获取access_token失败，请检查app_id和app_secret是否正确')
        os.system("pause")
        sys.exit(1)
    return access_token


def get_color():
    # 往list中填喜欢的颜色即可
    color_list = ['#6495ED', '#3CB371', "#3B99D4", "#8ED14B", "#F06B49", "#ECC2F1", "#82C7C3", "#E3698A", "#1776EB", "#F5B2AC", "#533085", "#89363A", "#19413E", "#D92B45", "#60C9FF", "#1B9F2E", "#BA217D", "#076B82"]
    return random.choice(color_list)


def send_wechat_message(to_user, now_time, title, detail, url, wx_post_url):
    data = {
        "touser": to_user,
        "template_id": read_yaml('template_id'),
        "url": url,
        "topcolor": "#FF0000",
        "data": {
            "title_title": {
                "value": "通知内容：  ",
                "color": "#a9a9a9"
            },
            "title": {
                "value": title,
                "color": get_color()
            },
            "now_time_title": {
                "value": "\n通知时间：  ",
                "color": "#a9a9a9"
            },
            "now_time": {
                "value": now_time,
                "color": get_color()
            },
            "detail_title": {
                "value": "\n通知内容：  ",
                "color": "#a9a9a9"
            },
            "detail": {
                "value": detail,
                "color": get_color()
            }
        }
    }
    headers = {
        'Content-Type': 'application/json',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) '
        'AppleWebKit/537.36 (KHTML, like Gecko) Chrome/103.0.0.0 Safari/537.36'
    }
    response = requests.post(wx_post_url, headers=headers, json=data).json()
    if response["errcode"] == 40037:
        logging.error(now_time + '推送消息失败，请检查模板id是否正确')
    elif response["errcode"] == 40036:
        logging.error(now_time + '推送消息失败，请检查模板id是否为空')
    elif response["errcode"] == 40003:
        logging.error(now_time + '推送消息失败，请检查微信号是否正确')
    elif response["errcode"] == 0:
        logging.info(now_time + '推送消息成功')
    else:
        logging.info(response)


def check_rss(rss_uri, push_id, id):
    bili_url = read_yaml('rss_hub_service', 'config.yaml') + rss_uri
    rss_data = Rss.objects.get(id=id)
    d = feedparser.parse(bili_url)
    detail = d['entries'][0]['summary']
    title = d['entries'][0]['title']
    link = d['entries'][0]['link']
    time = d['entries'][0]['published']
    rss_timestamp = int(dt.strptime(time, '%a, %d %b %Y %H:%M:%S %Z').timestamp())
    now_time = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    if rss_data.timestamp != str(rss_timestamp):
        push_data = Push.objects.get(id=push_id)
        if push_data.push_type == 'ding':
            send_ding_message(push_data.ding_access_token, push_data.ding_keyword, now_time, title, link)
        if push_data.push_type == 'wechat':
            ACCESS_TOKEN = get_wechat_access_token(push_data.app_id, push_data.app_secret, now_time)
            wx_post_url = "https://api.weixin.qq.com/cgi-bin/message/template/send?access_token=" + ACCESS_TOKEN
            for i in push_data.to_user_ids:
                send_wechat_message(i, now_time, title, detail, link, wx_post_url)
        rss_data.timestamp = str(rss_timestamp)
        rss_data.save()
    else:
        logging.info(str(id) + "当前没有推送")


class PushView(APIView):
    authentication_classes = [JWTAuthentication, ]

    def __init__(self, **kwargs):
        super().__init__(kwargs)
        self.user = None
        self.GET = None
        self.META = None
        self.body = None

    add_push_request_body = openapi.Schema(
        type=openapi.TYPE_OBJECT,
        required=['push_type', 'rss_id', 'ding_access_token', 'ding_keyword', 'wechat_template_id', 'wechat_app_id', 'wechat_to_user_ids'],
        properties={
            'rss_id': openapi.Schema(type=openapi.TYPE_INTEGER, description='rss表的id'),
            'detection_time': openapi.Schema(type=openapi.TYPE_STRING, description='检测的时间(分钟）'),
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
        data = json.loads(self.body.decode('utf-8'))
        if data.get('push_type') is None or data.get('rss_id') is None or data.get('detection_time') is None:
            logging.error(error_response.missing_parameter.value['message'])
            return JsonResponse(error_response.missing_parameter.value)
        else:
            rss_id = data['rss_id']
            push_type = data['push_type']
            detection_time = data['detection_time']
            rss_push_id = Rss.objects.get(id=rss_id).push_id
            if not rss_push_id is None or rss_push_id == '':
                logging.error(error_response.push_full_error_parameter.value['message'])
                return JsonResponse(error_response.push_full_error_parameter.value)
            else:
                if push_type == 'ding':
                    if data.get('ding_access_token') is None or data.get('ding_keyword') is None:
                        logging.error(error_response.missing_parameter.value['message'])
                        return JsonResponse(error_response.missing_parameter.value)
                    else:
                        ding_access_token = data['ding_access_token']
                        ding_keyword = data['ding_keyword']
                        create_push = Push.objects.create(push_type=push_type, ding_access_token=ding_access_token, ding_keyword=ding_keyword)
                        data = Rss.objects.get(id=rss_id)
                        data.push_id = create_push.id
                        data.detection_time = detection_time
                        data.save()
                        logging.info('用户' + str(self.user.id) + '已新增push')
                        Response = {
                            "code": 0,
                            "message": "新增成功"
                        }
                        if not TEST:
                            requests.get(url='http://127.0.0.1:8000/api/push/refresh')
                elif push_type == 'wechat':
                    if data.get('wechat_template_id') is None or data.get('wechat_app_id') is None or data.get('wechat_to_user_ids') is None:
                        logging.error(error_response.missing_parameter.value['message'])
                        return JsonResponse(error_response.missing_parameter.value)
                    else:
                        wechat_template_id = data['wechat_template_id']
                        wechat_app_id = data['wechat_app_id']
                        wechat_to_user_ids = data['wechat_to_user_ids']
                        create_push = Push.objects.create(push_type=push_type, wechat_template_id=wechat_template_id, wechat_app_id=wechat_app_id, wechat_to_user_ids=wechat_to_user_ids)
                        data = Rss.objects.get(id=rss_id)
                        data.push_id = create_push.id
                        data.save()
                        logging.info('用户' + str(self.user.id) + '已新增push')
                        Response = {
                            "code": 0,
                            "message": "新增成功"
                        }
                        if not TEST:
                            requests.get(url='http://127.0.0.1:8000/api/push/refresh')
                else:
                    logging.error(error_response.push_error_parameter.value['message'])
                    return JsonResponse(error_response.push_error_parameter.value)
        return JsonResponse(Response)

    edit_push_request_body = openapi.Schema(
        type=openapi.TYPE_OBJECT,
        required=['id', 'push_type', 'ding_access_token', 'ding_keyword', 'wechat_template_id', 'wechat_app_id', 'wechat_to_user_ids'],
        properties={
            'id': openapi.Schema(type=openapi.TYPE_INTEGER, description='id'),
            'push_type': openapi.Schema(type=openapi.TYPE_STRING, description='钉钉推送还是微信测试号推送(钉钉：ding，微信测试号：wechat)"'),
            'ding_access_token': openapi.Schema(type=openapi.TYPE_STRING, description='钉钉参数'),
            'ding_keyword': openapi.Schema(type=openapi.TYPE_STRING, description='钉钉自定义关键词'),
            'wechat_template_id': openapi.Schema(type=openapi.TYPE_STRING, description='微信模板id'),
            'detection_time': openapi.Schema(type=openapi.TYPE_STRING, description='检测的时间(分钟）'),
            'wechat_app_id': openapi.Schema(type=openapi.TYPE_STRING, description='微信appId'),
            'wechat_to_user_ids': openapi.Schema(type=openapi.TYPE_STRING, description='微信发送的用户们'),
        })

    @swagger_auto_schema(value='/api/push/edit', method='put', operation_summary='编辑推送接口', request_body=edit_push_request_body, responses={0: base_access_response_schema, 201: 'None'})
    @csrf_exempt
    @api_view(['PUT'])
    def edit_push(self):
        data = json.loads(self.body.decode('utf-8'))
        if data.get('push_type') is None or data.get('id') is None:
            logging.error(error_response.missing_parameter.value['message'])
            return JsonResponse(error_response.missing_parameter.value)
        else:
            id = data['id']
            push_type = data['push_type']
            if push_type == 'ding':
                if data.get('ding_access_token') is None or data.get('ding_keyword') is None or data.get('detection_time') is None:
                    logging.error(error_response.missing_parameter.value['message'])
                    return JsonResponse(error_response.missing_parameter.value)
                else:
                    ding_access_token = data['ding_access_token']
                    ding_keyword = data['ding_keyword']
                    detection_time = data['detection_time']
                    data = Push.objects.get(id=id)
                    rss_data = Rss.objects.get(push_id=id)
                    data.ding_keyword = ding_keyword
                    data.ding_access_token = ding_access_token
                    rss_data.detection_time = detection_time
                    data.save()
                    rss_data.save()
                    logging.info('用户' + str(self.user.id) + '已修改push' + str(id))
                    Response = {
                        "code": 0,
                        "message": "修改成功"
                    }
                    if not TEST:
                        requests.get(url='http://127.0.0.1:8000/api/push/refresh')
            elif push_type == 'wechat':
                if data.get('wechat_template_id') is None or data.get('wechat_app_id') is None or data.get('wechat_to_user_ids') is None or data.get('detection_time') is None:
                    logging.error(error_response.missing_parameter.value['message'])
                    return JsonResponse(error_response.missing_parameter.value)
                else:
                    wechat_template_id = data['wechat_template_id']
                    wechat_app_id = data['wechat_app_id']
                    wechat_to_user_ids = data['wechat_to_user_ids']
                    detection_time = data['detection_time']
                    data = Push.objects.get(id=id)
                    rss_data = Rss.objects.get(push_id=id)
                    data.wechat_template_id = wechat_template_id
                    data.wechat_app_id = wechat_app_id
                    data.wechat_to_user_ids = wechat_to_user_ids
                    rss_data.detection_time = detection_time
                    data.save()
                    rss_data.save()
                    logging.info('用户' + str(self.user.id) + '已修改push' + str(id))
                    Response = {
                        "code": 0,
                        "message": "修改成功"
                    }
                    if not TEST:
                        requests.get(url='http://127.0.0.1:8000/api/push/refresh')
            else:
                logging.error(error_response.push_error_parameter.value['message'])
                return JsonResponse(error_response.push_error_parameter.value)
        return JsonResponse(Response)

    delete_push_request_body = openapi.Schema(
        type=openapi.TYPE_OBJECT,
        required=['push_type'],
        properties={
            'rss_id': openapi.Schema(type=openapi.TYPE_INTEGER, description='rss表的id'),
        })

    @swagger_auto_schema(value='/api/push/delete', method='delete', operation_summary='删除推送接口', request_body=delete_push_request_body, responses={0: base_access_response_schema, 201: 'None'})
    @csrf_exempt
    @api_view(['DELETE'])
    def delete_push(self):
        data = json.loads(self.body.decode('utf-8'))
        if data.get('rss_id') is None:
            logging.error(error_response.missing_parameter.value['message'])
            return JsonResponse(error_response.missing_parameter.value)
        else:
            rss_id = data['rss_id']
            data = Rss.objects.get(id=rss_id)
            push_id = data.push_id
            data.push_id = None
            data.save()
            if Push.objects.get(id=push_id).delete():
                logging.info('用户' + str(self.user.id) + '已删除push' + str(rss_id))
                Response = {
                    "code": 0,
                    "message": "删除成功"
                }
                if not TEST:
                    requests.get(url='http://127.0.0.1:8000/api/push/refresh')
            else:
                logging.error(error_response.delete_error.value['message'])
                return JsonResponse(error_response.delete_error.value)
        return JsonResponse(Response)

    push_view_query_param = [
        openapi.Parameter('rss_id', openapi.IN_QUERY, type=openapi.TYPE_INTEGER, description="rss表的id"),
    ]

    push_view_access_response_schema = openapi.Response(
        description='Successful response',
        schema=openapi.Schema(type=openapi.TYPE_OBJECT, properties={
            'code': openapi.Schema(type=openapi.TYPE_INTEGER, description='code'),
            'message': openapi.Schema(type=openapi.TYPE_STRING, description='message'),
            'data': openapi.Schema(type=openapi.TYPE_OBJECT, description='data', properties={
                'id': openapi.Schema(type=openapi.TYPE_INTEGER, description='push_id'),
                'push_type': openapi.Schema(type=openapi.TYPE_STRING, description='钉钉推送还是微信测试号推送(钉钉：ding，微信测试号：wechat)'),
                'ding_access_token': openapi.Schema(type=openapi.TYPE_STRING, description='钉钉参数'),
                'ding_keyword': openapi.Schema(type=openapi.TYPE_STRING, description='钉钉自定义关键词'),
                'wechat_template_id': openapi.Schema(type=openapi.TYPE_STRING, description='微信模板id'),
                'wechat_app_id': openapi.Schema(type=openapi.TYPE_STRING, description='微信appId'),
                'detection_time': openapi.Schema(type=openapi.TYPE_STRING, description='检测的时间(分钟）'),
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
            "id": "",
            "detection_time": "",
        }
        rss_id = self.GET.get('rss_id')
        if rss_id is None or rss_id == '':
            logging.error(error_response.missing_parameter.value['message'])
            return JsonResponse(error_response.missing_parameter.value)
        else:
            rss_push_id = Rss.objects.get(id=rss_id).push_id
            if rss_push_id is None or rss_push_id == '':
                logging.info('用户' + str(self.user.id) + 'push' + str(rss_push_id) + '无推送配置')
                return success_response(0, "无推送配置", data)
            else:
                push_data = Push.objects.get(id=rss_push_id)
                rss_data = Rss.objects.get(id=rss_id)
                data['push_type'] = push_data.push_type
                data['ding_access_token'] = push_data.ding_access_token
                data['ding_keyword'] = push_data.ding_keyword
                data['wechat_template_id'] = push_data.wechat_template_id
                data['wechat_to_user_ids'] = push_data.wechat_to_user_ids
                data['detection_time'] = rss_data.detection_time
                data['id'] = push_data.id
                logging.info('用户' + str(self.user.id) + 'push' + str(rss_push_id) + '获取成功')
                return success_response(0, "获取成功", data)

    @swagger_auto_schema(value='/api/push/refresh', method='get', operation_summary='刷新推送接口', responses={0: base_access_response_schema, 201: 'None'})
    @csrf_exempt
    @api_view(['GET'])
    def refresh_push(self):
        rss_all = Rss.objects.all()
        try:
            old_tasks = settings.SCHEDULER.get_jobs()
            for task in old_tasks:
                task.remove()
        except Exception as e:
            print(f"Error clearing schedule: {e}")
        for i in rss_all:
            if not i.push_id is None or i.push_id == '':
                settings.SCHEDULER.add_job(check_rss, 'interval', seconds=i.detection_time * 60, args=(i.rss_uri, i.push_id, i.id))
        logging.info('刷新成功')
        Response = {
            "code": 0,
            "message": "刷新成功",
        }
        return JsonResponse(Response)

