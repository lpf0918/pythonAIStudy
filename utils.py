from flask import jsonify

def api_response(code=200, message="success", data=None):
    """
    统一的 API 响应封装函数
    :param code: 业务状态码 (默认 200)
    :param message: 提示信息 (默认 success)
    :param data: 返回的具体数据 (默认 None)
    """
    return jsonify({
        "code": code,
        "message": message,
        "data": data
    }), code  # 同时返回 JSON 内容和对应的 HTTP 状态码