from datetime import datetime
from typing import List, Union, Iterator

from data import QuestionTypeRepository, SubmissionAnswerRepository, SubmissionRepository, AnswerRepository, \
    FormTypeRepository
from data.db import Transaction
from data.entities import User, QuestionType, Question, SubmissionAnswer, Submission, Answer, Form, FormType
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

    def check(self, question: Question, answers: List[Union[int, str]]) -> float:
        return 1

    def supports_checking(self) -> bool:
        return False


def _calculate_score(question: Question, answers: List[int]):
    right_answer_ids = set(a.id for a in question.answers if a.is_right)
    score = sum(1 if a_id in right_answer_ids else -1 for a_id in answers)
    score /= len(right_answer_ids)
    return max(0, min(score, 1))


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

    def supports_checking(self) -> bool:
        return True

    def check(self, question: Question, answers: List[Union[int, str]]) -> float:
        return _calculate_score(question, answers)


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

    def supports_checking(self) -> bool:
        return True

    def check(self, question: Question, answers: List[Union[int, str]]) -> float:
        return _calculate_score(question, answers)


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


def _form_type_supports_checking(form_type: FormType):
    return form_type.id == FormTypeRepository.test.id


class SubmissionInfo:
    def __init__(self, submission: Submission):
        if submission.form is None:
            raise AssertionError("Form is not loaded")
        form = submission.form
        self.form_id = form.id
        self.form_title = form.title
        self.form_type = form.form_type.name
        self.time = submission.time
        self.score = submission.score if _form_type_supports_checking(form.form_type) else None


class SubmissionManager:
    @staticmethod
    def get_submissions_by_user(user: User) -> Iterator[SubmissionInfo]:
        return map(SubmissionInfo, SubmissionRepository.get_by_user_join_forms(user))

    @staticmethod
    def submit(user: User, form_id: int, answers: List[List[Union[int, str]]]) -> None:
        form = FormManager.get_form_by_id(user, form_id, True)
        if not form.is_public:
            raise PermissionError('Form is not published')

        if len(form.questions) != len(answers):
            raise ValueError('Question count mismatch')

        with Transaction.open() as tr:
            submission = Submission(None, datetime.now(), 0, form, user)
            SubmissionRepository.insert(submission)
            cnt_checked = 0
            score_sum = 0
            check_score = _form_type_supports_checking(form.form_type)
            for q, a in zip(form.questions, answers):
                handler = _get_handler(q)
                if handler is None:
                    raise ValueError('BUG: Unsupported question type')
                if not handler.validate_answers(q, a):
                    raise ValueError('Illegal answer')

                if check_score and handler.supports_checking():
                    cnt_checked += 1
                    score_sum += handler.check(q, a)

                handler.submit_answers(submission.id, q.id, a)

            if check_score and cnt_checked != 0:
                score = score_sum / cnt_checked
                submission.score = score
                SubmissionRepository.update(submission)

            tr.commit()
