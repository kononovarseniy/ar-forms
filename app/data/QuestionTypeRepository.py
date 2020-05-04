from typing import Optional

from data.db import open_cursor
from data.entities import QuestionType
from data.fieldset import EntityFields


class QuestionTypeRepository:
    fields = EntityFields(['id', 'name'], QuestionType, 'question_types')

    @staticmethod
    def get_by_id(type_id: int) -> Optional[QuestionType]:
        fields = QuestionTypeRepository.fields
        with open_cursor() as (conn, cur):
            cur.execute(f"SELECT {fields} FROM question_types WHERE id = %s", [type_id])
            return fields.unpack(fields)

    @staticmethod
    def get_by_name(name: str) -> Optional[QuestionType]:
        fields = QuestionTypeRepository.fields
        with open_cursor() as (conn, cur):
            cur.execute(f"SELECT {fields} FROM question_types WHERE name = %s", [name])
            return fields.unpack(fields)
