#coding=utf-8
import random, datetime, os, sys, json, requests, logging, feedparser, schedule, time
from util.yaml_util import read_yaml, read_all_yaml, write_yaml_value
from datetime import datetime as dt

test = False

if test:
    logging.basicConfig(level=logging.DEBUG)
else:
    logging.basicConfig(level=logging.INFO)


# 公众号的跳转链接
jump_url = "https://space.bilibili.com/" + str(read_yaml('uid')) + "/dynamic"

bili_url = "http://" + read_yaml('ip') + ":1200/bilibili/user/dynamic/" + str(read_yaml('uid'))


def get_rss():
    d = feedparser.parse(bili_url)
    post_data_detail = d['entries'][0]['summary']
    post_data_title = d['entries'][0]['title']
    post_data_link = d['entries'][0]['link']
    time = d['updated']
    timestamp = int(dt.strptime(time, '%a, %d %b %Y %H:%M:%S %Z').timestamp())
    post_data = {
        "title": post_data_title,
        "detail": post_data_detail,
        "timestamp": timestamp,
        "link": post_data_link,
    }
    return json.dumps(post_data, ensure_ascii=False)


def get_wechat_access_token(app_id, app_secret, now_time):
    # appId
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


def main():
    now_time = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    rss_data = json.loads(get_rss())
    title = rss_data['title']
    detail = rss_data['detail']
    link = rss_data['link']
    timestamp = rss_data['timestamp']

    if title == read_yaml('title'):
        logging.info(now_time + "主播没有发新动态")
    else:
        data = read_all_yaml()
        data.update({'timestamp': timestamp})
        if not test:
            write_yaml_value(data)
        if read_yaml('send_type') == 'wechat':
            ACCESS_TOKEN = get_wechat_access_token(read_yaml('app_id'), read_yaml('app_secret'), now_time)
            wx_post_url = "https://api.weixin.qq.com/cgi-bin/message/template/send?access_token=" + ACCESS_TOKEN
            for i in read_yaml('to_user_ids'):
                send_wechat_message(i, now_time, title, detail, jump_url, wx_post_url)
        elif read_yaml('send_type') == 'ding':
            send_ding_message(read_yaml('ding_access_token'), read_yaml('ding_keyword'), now_time, title, link)


if __name__ == "__main__":
    main()
    if not test:
        schedule.every(eval(read_yaml('detection_time'))).seconds.do(main)
        try:
            while True:
                schedule.run_pending()
                time.sleep(1)
        except:
            pass