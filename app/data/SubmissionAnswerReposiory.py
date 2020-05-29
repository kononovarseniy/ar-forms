from typing import Union, Iterator

from data.db import open_cursor
from data.entities import SubmissionAnswer, Submission
from data.fieldset import EntityFields


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
    def get_by_submissions(submission: Union[int, Submission]) -> Iterator[SubmissionAnswer]:
        fs = SubmissionAnswerRepository.fields

        submission_id = int(submission)
        with open_cursor() as cur:
            cur.execute(
                f"SELECT {fs} "
                "FROM submission_answers "
                "WHERE submission_answers.submission_id = %s",
                [submission_id])
            for submission in fs.unpack_iter(cur):
                yield submission
