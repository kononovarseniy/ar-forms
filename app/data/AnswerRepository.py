from itertools import repeat
from typing import Iterator, Collection

from data.db import open_cursor
from data.entities import Answer
from data.fieldset import EntityFields


class AnswerRepository:
    fields = EntityFields(['id', 'index', 'text', 'is_right', 'is_user_variant', 'question_id'], Answer, 'answers')

    @staticmethod
    def get_by_id(answer_id: int) -> Answer:
        fields = AnswerRepository.fields
        with open_cursor() as (conn, cur):
            cur.execute(f"SELECT {fields} FROM answers WHERE answers.id = %s", [answer_id])
            return fields.unpack(cur.fetchone())

    @staticmethod
    def get_all_by_question_id(question_id: int) -> Iterator[Answer]:
        fields = AnswerRepository.fields
        with open_cursor() as (conn, cur):
            cur.execute(f"SELECT {fields} FROM answers WHERE question_id = %s", [question_id])
            for q in fields.unpack_iter(cur):
                yield q

    @staticmethod
    def insert(answer: Answer):
        with open_cursor() as (conn, cur):
            cur.execute(
                "INSERT INTO answers(index, text, is_right, is_user_variant, question_id)"
                "VALUES (%s, %s, %s, %s, %s)"
                "RETURNING id;",
                (answer.index, answer.text, answer.is_right, answer.is_user_variant, answer.question_id))
            answer.id = cur.fetchone()[0]
            conn.commit()

    @staticmethod
    def update(answer: Answer):
        with open_cursor() as (conn, cur):
            cur.execute(
                "UPDATE answers "
                "SET index = %s, text = %s, is_right = %s, is_user_variant = %s, question_id = %s "
                "WHERE answers.id = %s;",
                (answer.index, answer.text, answer.is_right, answer.is_user_variant, answer.question_id, answer.id))
            conn.commit()

    @staticmethod
    def update_or_insert(answer: Answer):
        if answer.id:
            AnswerRepository.update(answer)
        else:
            AnswerRepository.insert(answer)

    @staticmethod
    def delete_all_by_ids(ids: Collection[int]):
        with open_cursor() as (conn, cur):
            ids_template = ','.join(repeat('%s', len(ids)))
            cur.execute(f"DELETE FROM answers WHERE id IN ({ids_template});", ids)
            conn.commit()
