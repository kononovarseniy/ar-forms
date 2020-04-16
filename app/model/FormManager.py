from datetime import datetime
from typing import Iterator, Any, Dict, List

from data import FormRepository, FormTypeRepository
from data.entities import User, Form


class FormManager:
    @staticmethod
    def is_accessible(requesting: User, form: Form):
        return form.is_public or (requesting and form.creator_id == requesting.id)

    @staticmethod
    def filter_accessible(requesting: User, forms: Iterator[Form]) -> Iterator[Form]:
        return filter(lambda f: FormManager.is_accessible(requesting, f), forms)

    @staticmethod
    def get_forms_by_user(requesting: User, user: User):
        return FormManager.filter_accessible(requesting, FormRepository.get_forms_by_creator(user))

    @staticmethod
    def get_form_by_id(requesting: User, form_id: int) -> Form:
        form = FormRepository.get_form_by_id(form_id)
        if form and not FormManager.is_accessible(requesting, form):
            raise PermissionError
        return form

    @staticmethod
    def update_form(requesting: User, updates: Dict[str, Any]):
        if not requesting:
            raise PermissionError

        form_id = updates.get('id', None)
        form_id = int(form_id)
        state = updates['state']

        # Get or create form
        if state == 'created':
            form = Form(None, "", "", FormTypeRepository.poll, requesting, datetime.now(), False)
        elif state == 'modified' or state == 'deleted':
            if not form_id or form_id <= 0:
                raise KeyError("No such form")
            form = FormRepository.get_form_by_id(form_id)
            if not form:
                raise KeyError("Form not found")
            if requesting.id != form.creator_id:
                raise PermissionError
            if state == 'modified' and form.is_public:
                raise ValueError("Cannot modify published form")
        else:
            raise ValueError("Invalid state")

        # Delete form
        if state == 'deleted':
            FormRepository.delete_form_by_id(form_id)
            return None

        # Set form fields
        if 'title' in updates:
            form.title = updates['title']
        if 'description' in updates:
            form.description = updates['description']
        if 'form_type' in updates:
            ft = updates['form_type']
            if ft == 'poll':
                form.set_form_type(FormTypeRepository.poll)
            elif ft == 'test':
                form.set_form_type(FormTypeRepository.test)
            else:
                raise ValueError("Invalid form type")
        if 'is_public' in updates:
            form.is_public = bool(updates['is_public'])

        # TODO: update_questions

        FormRepository.update_or_insert(form)

        return form
