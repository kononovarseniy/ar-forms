from flask import json

from data.entities import Form, FormType, User


class JSONEncoder(json.JSONEncoder):
    def default(self, o):
        if isinstance(o, Form):
            d = {
                'id': o.id,
                'title': o.title,
                'description': o.description,
                'form_type': o.form_type.name,
                'creation_date': o.creation_date,
                'is_public': o.is_public
            }
            if o.creator:
                d['creator'] = o.creator
            return d
        elif isinstance(o, FormType):
            return {
                'id': o.id,
                'name': o.name
            }
        elif isinstance(o, User):
            return {
                'id': o.id,
                'login': o.login,
                'display_name': o.display_name
            }
        else:
            return json.JSONEncoder.default(self, o)
