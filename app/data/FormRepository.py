from typing import List, Iterator

from data import FormTypeRepository
from data.db import open_cursor
from data.entities import Form
from data.fieldset import EntityFields, FieldSet


class FormRepository:
    fields = EntityFields(
        ['id', 'title', 'description', 'type_id', 'creator_id', 'creation_date', 'is_public'],
        Form, 'forms')

    @staticmethod
    def get_form_by_id(form_id: int) -> Form:
        fields = FieldSet(FormRepository.fields, FormTypeRepository.fields)
        fields.constructor = Form.set_form_type

        with open_cursor() as (conn, cur):
            cur.execute(
                f"SELECT {fields} "
                "FROM forms JOIN form_types ON forms.type_id = form_types.id "
                "WHERE forms.id = %s",
                [form_id])
            return fields.unpack(cur.fetchone())

    @staticmethod
    def insert(form: Form):
        with open_cursor() as (conn, cur):
            cur.execute(
                "INSERT INTO forms(title, description, type_id, creator_id, creation_date, is_public)"
                "VALUES (%s, %s, %s, %s, %s, %s)"
                "RETURNING id;",
                (form.title, form.description, form.form_type_id, form.creator_id, form.creation_date, form.is_public))
            form.id = cur.fetchone()[0]
            conn.commit()

    @staticmethod
    def update(form: Form):
        with open_cursor() as (conn, cur):
            cur.execute(
                "UPDATE forms "
                "SET title = %s, description = %s, type_id = %s, creator_id = %s, "
                "    creation_date = %s, is_public = %s "
                "WHERE id = %s;",
                (form.title, form.description, form.form_type_id, form.creator_id, form.creation_date, form.is_public,
                 form.id))
            conn.commit()

    @staticmethod
    def update_or_insert(form: Form):
        if form.id:
            FormRepository.update(form)
        else:
            FormRepository.insert(form)

    @staticmethod
    def delete_form_by_id(form_id):
        with open_cursor() as (conn, cur):
            cur.execute(
                "DELETE FROM forms WHERE id = %s;",
                (form_id,))
            conn.commit()

    @staticmethod
    def get_forms_by_creator(creator) -> Iterator[Form]:
        fs = FieldSet(FormRepository.fields, FormTypeRepository.fields)
        fs.constructor = Form.set_form_type

        creator_id = int(creator)
        with open_cursor() as (conn, cur):
            cur.execute(
                f"SELECT {fs} "
                "FROM forms JOIN form_types ON forms.type_id = form_types.id "
                "WHERE forms.creator_id = %s ORDER BY forms.creation_date DESC",
                (creator_id,))
            for form in list(fs.unpack_iter(cur)):
                yield form
