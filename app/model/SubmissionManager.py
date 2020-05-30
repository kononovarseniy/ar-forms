from datetime import datetime
from typing import List, Union

from data import QuestionTypeRepository, SubmissionAnswerRepository, SubmissionRepository, AnswerRepository
from data.db import Transaction
from data.entities import User, QuestionType, Question, SubmissionAnswer, Submission, Answer
from model import FormManager

single_variant = QuestionTypeRepository.get_by_name('single-variant')
multiple_variants = QuestionTypeRepository.get_by_name('multiple-variants')
free_answer = QuestionTypeRepository.get_by_name('free-answer')


class AnswerHandler:
    def get_accepted_type(self) -> QuestionType:
        pass

    def validate_answers(self, question: Question, answers: List[Union[int, str]]) -> bool:
        pass

    def submit_answers(self, submission_id: int, question_id: int, answers: List[Union[int, str]]):
        pass


class SingleVariantAnswerHandler(AnswerHandler):
    def get_accepted_type(self) -> QuestionType:
        return single_variant

    def validate_answers(self, question: Question, answers: List[Union[int, str]]) -> bool:
        if len(answers) != 1:
            return False

        answer = answers[0]
        if not isinstance(answer, int):
            return False

        return any(a.id == answer for a in question.answers)

    def submit_answers(self, submission_id: int, question_id: int, answers: List[Union[int, str]]):
        for a in answers:
            SubmissionAnswerRepository.insert(SubmissionAnswer(submission_id, a))


class MultipleVariantsAnswerHandler(AnswerHandler):
    def get_accepted_type(self) -> QuestionType:
        return multiple_variants

    def validate_answers(self, question: Question, answers: List[Union[int, str]]) -> bool:
        if not all(isinstance(a, int) for a in answers):
            return False

        return set(answers).issubset(a.id for a in question.answers)

    def submit_answers(self, submission_id: int, question_id: int, answers: List[Union[int, str]]):
        for a in answers:
            SubmissionAnswerRepository.insert(SubmissionAnswer(submission_id, a))


class FreeAnswerHandler(AnswerHandler):
    def get_accepted_type(self) -> QuestionType:
        return free_answer

    def validate_answers(self, question: Question, answers: List[Union[int, str]]) -> bool:
        if len(answers) != 1:
            return False

        return isinstance(answers[0], str)

    def submit_answers(self, submission_id: int, question_id: int, answers: List[Union[int, str]]):
        answer = Answer(None, 0, answers[0], False, True, question_id)
        AnswerRepository.insert(answer)
        SubmissionAnswerRepository.insert(SubmissionAnswer(submission_id, answer))


_handlers = [
    SingleVariantAnswerHandler(),
    MultipleVariantsAnswerHandler(),
    FreeAnswerHandler()
]


def _get_handler(q: Question):
    return next((h for h in _handlers if h.get_accepted_type().name == q.question_type.name), None)


class SubmissionManager:
    @staticmethod
    def submit(user: User, form_id: int, answers: List[List[Union[int, str]]]) -> None:
        form = FormManager.get_form_by_id(user, form_id, False)
        if not form.is_public:
            raise PermissionError('Form is not published')

        if len(form.questions) != len(answers):
            raise ValueError('Question count mismatch')

        with Transaction.open() as tr:
            submission = Submission(None, datetime.now(), form, user)
            SubmissionRepository.insert(submission)
            for q, a in zip(form.questions, answers):
                handler = _get_handler(q)
                if handler is None:
                    raise ValueError('BUG: Unsupported question type')
                if not handler.validate_answers(q, a):
                    raise ValueError('Illegal answer')
                handler.submit_answers(submission.id, q.id, a)
            tr.commit()
