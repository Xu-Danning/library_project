from flask import jsonify

class APIError(Exception):
    def __init__(self, message, status_code=400):
        super().__init__(message)
        self.message = message
        self.status_code = status_code


def validate_json(required_fields, data):
    """简单字段存在性与类型检查（非常轻量）"""
    errors = []
    for k, t in required_fields.items():
        if k not in data:
            errors.append(f"Missing field: {k}")
        else:
            if t and data[k] is not None and not isinstance(data[k], t):
                errors.append(f"Field {k} expected {t.__name__}")
    if errors:
        raise APIError('; '.join(errors), status_code=400)


def json_response(payload=None, status=200):
    if payload is None:
        payload = {}
    return jsonify(payload), status
