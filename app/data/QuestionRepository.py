from itertools import repeat
from typing import Collection, Iterator

from data import QuestionTypeRepository
from data.db import open_cursor
from data.entities import Question
from data.fieldset import EntityFields, FieldSet


class QuestionRepository:
    fields = EntityFields(['id', 'index', 'text', 'type_id', 'form_id'], Question, 'questions')

    fields_with_type = FieldSet(fields, QuestionTypeRepository.fields)
    fields_with_type.constructor = Question.set_question_type

    @staticmethod
    def get_by_id(question_id: int) -> Question:
        fields = QuestionRepository.fields_with_type
        with open_cursor() as (conn, cur):
            cur.execute(f"SELECT {fields} "
                        f"FROM questions LEFT JOIN question_types on questions.type_id = question_types.id "
                        f"WHERE questions.id = %s", [question_id])
            return fields.unpack(cur.fetchone())

    @staticmethod
    def get_all_by_form_id(form_id: int) -> Iterator[Question]:
        fields = QuestionRepository.fields_with_type
        with open_cursor() as (conn, cur):
            cur.execute(f"SELECT {fields} "
                        f"FROM questions LEFT JOIN question_types on questions.type_id = question_types.id "
                        f"WHERE form_id = %s", [form_id])
            for q in fields.unpack_iter(cur):
                yield q

    @staticmethod
    def insert(question: Question):
        with open_cursor() as (conn, cur):
            cur.execute(
                "INSERT INTO questions(index, text, type_id, form_id)"
                "VALUES (%s, %s, %s, %s)"
                "RETURNING id;",
                (question.index, question.text, question.question_type_id, question.form_id))
            question.id = cur.fetchone()[0]
            conn.commit()

    @staticmethod
    def update(question: Question):
        with open_cursor() as (conn, cur):
            cur.execute(
                "UPDATE questions "
                "SET index = %s, text = %s, type_id = %s, form_id = %s "
                "WHERE id = %s;",
                (question.index, question.text, question.question_type_id, question.form_id, question.id))
            conn.commit()

    @staticmethod
    def update_or_insert(question: Question):
        if question.id:
            QuestionRepository.update(question)
        else:
            QuestionRepository.insert(question)

    @staticmethod
    def delete_all_by_ids(ids: Collection[int]):
        with open_cursor() as (conn, cur):
            ids_template = ','.join(repeat('%s', len(ids)))
            cur.execute(f"DELETE FROM questions WHERE id IN ({ids_template});", ids)
            conn.commit()
