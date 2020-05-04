from functools import wraps, cached_property
from typing import Optional, Tuple, Any

from flask import request, jsonify, json
from jsonschema import validate, ValidationError
from werkzeug.exceptions import BadRequestKeyError

from model import SessionManager, FormManager

_api_methods = {}


def api_method(func):
    def unpack_result(res: Optional[Any]) -> Tuple[Any, int, Optional[str]]:
        if res is None:
            result, status, error = {}, 200, None
        elif isinstance(res, tuple):
            result, status, error = res
        else:
            result, status, error = res, 200, None
        return result, status, error

    @wraps(func)
    def wrapper(*args, **kwargs):
        try:
            res = func(*args, **kwargs)
        except BadRequestKeyError as e:
            error = "Missing argument " + e.args[0]
            status = 400
        except ValidationError as e:
            error = e.message
            status = 400
        except KeyError as e:
            error = e.args[0]
            status = 300
        except ValueError as e:
            error = e.args[0] if len(e.args) != 0 else "Invalid value"
            status = 400
        except PermissionError as e:
            error = e.args[0] if len(e.args) != 0 else "Permission denied"
            status = 403
        else:
            return unpack_result(res)
        return None, status, error

    if func.__name__ in _api_methods:
        raise KeyError()

    _api_methods[func.__name__] = wrapper

    return wrapper


def auth_required(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        user = SessionManager.get_user()
        if not user:
            raise PermissionError("Authorization required")
        return func(user, *args, **kwargs)

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


@cached_property
def _update_form_schema():
    with open('schema/update_form_schema.json', 'r') as f:
        return json.loads(f.read())


@api_method
@auth_required
def update_form(user):
    updates_json = request.args['form']
    publish = request.args.get('publish', False)

    updates = json.loads(updates_json)
    validate(updates, _update_form_schema)

    form = FormManager.update_form(user, updates, publish)

    return form


@api_method
@auth_required
def delete_form(user):
    form_id = request.args['form_id']
    FormManager.delete_form(user, form_id)


@api_method
@auth_required
def publish_form(user):
    form_id = request.args['form_id']
    FormManager.delete_form(user, form_id)
