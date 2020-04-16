import functools

from flask import request, jsonify, json
from werkzeug.exceptions import BadRequestKeyError

from model import SessionManager, FormManager

_api_methods = {}


def api_method(func):
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        result, error, status = None, None, None
        try:
            res = func(*args, **kwargs)
        except BadRequestKeyError as e:
            error = "Missing argument " + e.args[0]
            status = 400
        except KeyError as e:
            error = e.args[0]
            status = 300
        except ValueError as e:
            error = e.args[0] if len(e.args) != 0 else "Invalid value"
            status = 400
        except PermissionError:
            error = "Permission denied"
            status = 403
        else:
            if isinstance(res, tuple):
                result, status, error = res
            else:
                result, status, error = res, 200, None
        return result, status, error

    if func.__name__ in _api_methods:
        raise KeyError()

    _api_methods[func.__name__] = wrapper

    return wrapper


def execute_api_method(method):
    result = None
    try:
        function = _api_methods[method]
    except KeyError:
        error = "Unknown method"
        status = 400
    else:
        result, status, error = function()

    if status == 200:
        return jsonify({
            'success': True,
            'result': result
        }), status
    else:
        return jsonify({
            'success': False,
            'error': error
        }), status


@api_method
def get_form():
    user = SessionManager.get_user()
    form_ids = int(request.args['form_id'])

    form = FormManager.get_form_by_id(user, form_ids)
    if form:
        return form
    else:
        return None, 404, 'Form not found'


@api_method
def update_form():
    user = SessionManager.get_user()
    updates_json = request.args['updates']

    updates = json.loads(updates_json)
    form = FormManager.update_form(user, updates)

    return form
