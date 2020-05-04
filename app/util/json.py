from flask import json

from data.entities import Form, FormType, User, Question, QuestionType, Answer


class JSONEncoder(json.JSONEncoder):
    def default(self, o):
        if isinstance(o, Form):
            d = {
                'id': o.id,
                'title': o.title,
                'description': o.description,
                'form_type': o.form_type,
                'creation_date': o.creation_date,
                'is_public': o.is_public,
                'questions': getattr(o, 'questions', [])
            }
            if o.creator:
                d['creator'] = o.creator
            return d
        elif isinstance(o, FormType):
            return o.name
        elif isinstance(o, User):
            return {
                'id': o.id,
                'login': o.login,
                'display_name': o.display_name
            }
        elif isinstance(o, Question):
            return {
                'id': o.id,
                'index': o.index,
                'text': o.text,
                'question_type': o.question_type,
                'form_id': o.form_id,
                'answers': getattr(o, 'answers', [])
            }
        elif isinstance(o, Answer):
            return {
                'id': o.id,
                'index': o.index,
                'text': o.text,
                'is_right': o.is_right,
                'is_user_variant': o.is_user_variant,
                'question_id': o.question_id
            }
        elif isinstance(o, QuestionType):
            return o.name
        else:
            return json.JSONEncoder.default(self, o)
