from typing import Union, Iterator

from data import AnswerRepository
from data.db import open_cursor
from data.entities import SubmissionAnswer, Submission
from data.fieldset import EntityFields, FieldSet


class SubmissionAnswerRepository:
    fields = EntityFields(
        ['submission_id', 'answer_id'],
        SubmissionAnswer, 'submission_answers')

    @staticmethod
    def insert(submission_answer: SubmissionAnswer):
        with open_cursor() as cur:
            cur.execute(
                "INSERT INTO submission_answers(submission_id, answer_id)"
                "VALUES (%s, %s);",
                [submission_answer.submission_id, submission_answer.answer_id])

    @staticmethod
    def get_by_submission_join_answers(submission: Union[int, Submission]) -> Iterator[SubmissionAnswer]:
        fs = FieldSet(SubmissionAnswerRepository.fields, AnswerRepository.fields)
        if isinstance(submission, Submission):
            fs.constructor = lambda sa, a: sa.set_submission(submission).set_answer(a)
        else:
            fs.constructor = lambda sa, a: sa.set_answer(a)

        submission_id = int(submission)
        with open_cursor() as cur:
            cur.execute(
                f"SELECT {fs} "
                "FROM submission_answers JOIN answers ON submission_answers.answer_id = answers.id "
                "WHERE submission_answers.submission_id = %s",
                [submission_id])
            for submission_answer in fs.unpack_iter(cur):
                yield submission_answer
