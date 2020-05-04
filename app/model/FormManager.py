from datetime import datetime
from typing import Iterator, Any, Dict, List, Optional

from data import FormRepository, FormTypeRepository
from data.entities import User, Form


class FormManager:
    @staticmethod
    def is_accessible(requesting: Optional[User], form: Form):
        return form.is_public or (requesting and form.creator_id == requesting.id)

    @staticmethod
    def is_owner(requesting: Optional[User], form: Form):
        return requesting and form.creator_id == requesting.id

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
    def delete_form(requesting: User, form_id: int) -> None:
        form = FormRepository.get_form_by_id(form_id)
        if not form:
            raise KeyError("No such form")
        if not FormManager.is_owner(requesting, form):
            raise PermissionError
        FormRepository.delete_form_by_id(form_id)

    @staticmethod
    def update_form(requesting: User, updates: Dict[str, Any]):
        if not requesting:
            raise PermissionError

        form_id = updates.get('id', None)
        is_new = form_id is None
        if form_id is not None:
            form_id = int(form_id)

        # Get or create form
        if is_new:
            form = Form(None, "", "", FormTypeRepository.poll, requesting, datetime.now(), False)
        else:
            form = FormRepository.get_form_by_id(form_id)
            if not form:
                raise KeyError("Form not found")
            if not FormManager.is_owner(requesting, form):
                raise PermissionError
            if form.is_public:
                raise ValueError("Cannot modify published form")

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
