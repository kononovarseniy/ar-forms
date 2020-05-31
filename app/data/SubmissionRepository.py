from typing import Iterator, Union

from data import UserRepository, FormRepository, FormTypeRepository
from data.db import open_cursor
from data.entities import Submission, Form, User
from data.fieldset import EntityFields, FieldSet


class SubmissionRepository:
    fields = EntityFields(
        ['id', 'time', 'score', 'form_id', 'user_id'],
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
                "INSERT INTO submissions(time, score, form_id, user_id)"
                "VALUES (%s, %s, %s, %s)"
                "RETURNING id;",
                [submission.time, submission.score, submission.form_id, submission.user_id])
            submission.id = cur.fetchone()[0]

    @staticmethod
    def update(submission: Submission):
        with open_cursor() as cur:
            cur.execute(
                "UPDATE submissions "
                "SET time = %s, score = %s, form_id = %s, user_id = %s "
                "WHERE id = %s;",
                [submission.time, submission.score, submission.form_id, submission.user_id, submission.id])

    @staticmethod
    def delete(submission: Union[int, Submission]):
        with open_cursor() as cur:
            cur.execute(
                "DELETE FROM submissions WHERE id = %s;",
                [int(submission)])

    @staticmethod
    def get_by_user_join_forms(user: Union[int, User]) -> Iterator[Submission]:
        fs = FieldSet(SubmissionRepository.fields, FormRepository.fields, FormTypeRepository.fields)

        if isinstance(user, User):
            fs.constructor = lambda s, f, ft: s.set_form(f.set_form_type(ft)).set_user(user)
        else:
            fs.constructor = lambda s, f, ft: s.set_form(f.set_form_type(ft))

        user_id = int(user)
        with open_cursor() as cur:
            cur.execute(
                f"SELECT {fs} "
                "FROM submissions "
                "JOIN forms on submissions.form_id = forms.id "
                "JOIN form_types ON forms.type_id = form_types.id "
                "WHERE submissions.user_id = %s ORDER BY submissions.time DESC",
                [user_id])
            for submission in fs.unpack_iter(cur):
                yield submission

    @staticmethod
    def get_by_form_join_users(form: Union[int, Form]) -> Iterator[Submission]:
        fs = FieldSet(SubmissionRepository.fields, UserRepository.fields)
        if isinstance(form, Form):
            fs.constructor = lambda s, u: s.set_form(form).set_user(u)
        else:
            fs.constructor = lambda s, u: s.set_user(u)

        form_id = int(form)
        with open_cursor() as cur:
            cur.execute(
                f"SELECT {fs} "
                "FROM submissions JOIN users on submissions.user_id = users.id "
                "WHERE submissions.form_id = %s ORDER BY submissions.time DESC",
                [form_id])
            for submission in fs.unpack_iter(cur):
                yield submission
