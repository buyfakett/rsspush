from django.http import JsonResponse


def success_response(code: int, message: str, data: object):
    """
    :param code:    string    code
    :param message: string    消息
    :param data:    object    数据
    """
    return JsonResponse({'code': code, 'message': message, 'data': data})
