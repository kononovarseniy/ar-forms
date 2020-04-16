from data.db import get_cursor, del_cursor, FORM_TYPE_POLL_ID, FORM_TYPE_TEST_ID
from data.entities import FormType
from data.fieldset import EntityFields


class FormTypeRepository:
    fields = EntityFields(['id', 'name'], FormType, 'form_types')
    poll = None
    test = None

    @staticmethod
    def get_form_type_by_id(type_id):
        conn, cur = get_cursor()
        cur.execute("SELECT id, name FROM form_types WHERE id = %s", (type_id,))
        fields = cur.fetchone()
        del_cursor(conn, cur)

        if fields:
            return FormType(*fields)


FormTypeRepository.poll = FormTypeRepository.get_form_type_by_id(FORM_TYPE_POLL_ID)
FormTypeRepository.test = FormTypeRepository.get_form_type_by_id(FORM_TYPE_TEST_ID)
