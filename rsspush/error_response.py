from enum import Enum
from django.http import JsonResponse


def success_response(code: int, message: str, data):
    return JsonResponse({'code': code, 'message': message, 'data': data})


class error_response(Enum):
    phone_error = {'code': 10001, 'message': "不是合法手机号码"}
    phone_repeat_error = {'code': 10002, 'message': "该手机号已被注册"}
    phone_not_found_error = {'code': 10003, 'message': "该手机号没有注册"}
    password_format_error = {'code': 10004, 'message': "以字母开头，长度在6~18之间，只能包含字母、数字和下划线"}
    password_error = {'code': 10006, 'message': "密码错误"}
    old_password_error = {'code': 10007, 'message': "旧密码错误"}
    delete_error = {'code': 10008, 'message': "删除失败"}
    add_rss_error = {'code': 10009, 'message': "新增rss失败"}
    missing_parameter = {'code': 10010, 'message': "参数缺少"}
    no_data = {'code': 10011, 'message': "没有这数据"}
    push_error_parameter = {'code': 10012, 'message': "没有这个推送选项"}
    push_full_error_parameter = {'code': 10013, 'message': "此rss已有push数据，应该调修改接口"}
