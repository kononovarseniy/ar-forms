from typing import Iterator, Union

from data.db import open_cursor
from data.entities import Submission, Form
from data.fieldset import EntityFields


class SubmissionRepository:
    fields = EntityFields(
        ['id', 'time', 'form_id', 'user_id'],
        Submission, 'submissions')

    @staticmethod
    def get_by_id(submission_id: int) -> Submission:
        fields = SubmissionRepository.fields
        with open_cursor() as cur:
            cur.execute(
                f"SELECT {fields} "
                "FROM submissions "
                "WHERE submissions.id = %s",
                [submission_id])
            return fields.unpack(cur.fetchone())

    @staticmethod
    def insert(submission: Submission):
        with open_cursor() as cur:
            cur.execute(
                "INSERT INTO submissions(time, form_id, user_id)"
                "VALUES (%s, %s, %s)"
                "RETURNING id;",
                [submission.time, submission.form_id, submission.user_id])
            submission.id = cur.fetchone()[0]

    @staticmethod
    def delete(submission: Union[int, Submission]):
        with open_cursor() as cur:
            cur.execute(
                "DELETE FROM submissions WHERE id = %s;",
                [int(submission)])

    @staticmethod
    def get_by_form(form: Union[int, Form]) -> Iterator[Submission]:
        fs = SubmissionRepository.fields

        form_id = int(form)
        with open_cursor() as cur:
            cur.execute(
                f"SELECT {fs} "
                "FROM submissions "
                "WHERE submissions.form_id = %s ORDER BY submissions.time DESC",
                [form_id])
            for submission in fs.unpack_iter(cur):
                yield submission
