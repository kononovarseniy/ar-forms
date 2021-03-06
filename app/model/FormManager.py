from datetime import datetime
from typing import Iterator, Any, Dict, Optional

from data import FormRepository, FormTypeRepository, QuestionRepository, AnswerRepository, QuestionTypeRepository
from data.db import Transaction
from data.entities import User, Form, Question, Answer


class FormManager:
    @staticmethod
    def is_accessible(requesting: Optional[User], form: Form):
        return form.is_public or (requesting and form.creator_id == requesting.id)

    @staticmethod
    def is_owner(requesting: Optional[User], form: Form):
        return requesting and form.creator_id == requesting.id

    @staticmethod
    def filter_accessible(requesting: User, forms: Iterator[Form]) -> Iterator[Form]:
        return filter(lambda f: FormManager.is_accessible(requesting, f), forms)

    @staticmethod
    def get_and_check_owner(requesting: User, form_id: int) -> Form:
        form = FormRepository.get_form_by_id(form_id)
        if not form:
            raise KeyError("No such form")
        if not FormManager.is_owner(requesting, form):
            raise PermissionError
        return form

    @staticmethod
    def get_forms_by_user(requesting: User, user: User):
        return FormManager.filter_accessible(requesting, FormRepository.get_forms_by_creator(user))

    @staticmethod
    def get_form_by_id(requesting: User, form_id: int, get_answers: bool) -> Form:
        form = FormRepository.get_form_by_id(form_id)
        if form is None:
            raise KeyError("No such form")
        if form and not FormManager.is_accessible(requesting, form):
            raise PermissionError

        form.questions = list(QuestionRepository.get_all_by_form_id(form_id))
        form.questions.sort(key=lambda x: x.index)
        for q in form.questions:
            q.answers = list(AnswerRepository.get_all_by_question_id(q.id))
            if not get_answers:
                for a in q.answers:
                    a.is_right = False
            q.answers.sort(key=lambda x: x.index)

        return form

    @staticmethod
    def delete_form(requesting: User, form_id: int) -> None:
        # Check form existence and access rights
        FormManager.get_and_check_owner(requesting, form_id)
        FormRepository.delete_form_by_id(form_id)

    @staticmethod
    def publish_form(requesting: User, form_id: int) -> None:
        form = FormManager.get_and_check_owner(requesting, form_id)
        form.is_public = True
        FormRepository.update_or_insert(form)

    @staticmethod
    def update_form(requesting: User, updates: Dict[str, Any], publish: bool) -> Form:
        if not requesting:
            raise PermissionError

        with Transaction.open() as tr:
            form = FormManager._update_form(updates, requesting, publish)
            tr.commit()
            return form

    @staticmethod
    def _update_form(updates: Dict[str, Any], user: User, publish: bool) -> Form:
        form_id = int(updates.get('id'))
        is_new = form_id == 0

        if is_new:
            form = Form(None, "", "", FormTypeRepository.poll, user, datetime.now(), False)
            old_form_questions = []
        else:
            form = FormRepository.get_form_by_id(form_id)
            if not form:
                raise KeyError("Form not found")
            if not FormManager.is_owner(user, form):
                raise PermissionError
            if form.is_public:
                raise ValueError("Cannot modify published form")
            old_form_questions = QuestionRepository.get_all_by_form_id(form_id)

        # Set form fields
        form.title = updates['title']
        form.description = updates['description']
        ft = updates['form_type']
        if ft == 'poll':
            form.set_form_type(FormTypeRepository.poll)
        elif ft == 'test':
            form.set_form_type(FormTypeRepository.test)
        else:
            raise ValueError("Invalid form type")
        form.is_public = publish

        # Insert it before questions. It allows us to to get valid id
        FormRepository.update_or_insert(form)

        unused_question_ids = set(q.id for q in old_form_questions)
        form.questions = []
        for i, q in enumerate(updates['questions']):
            unused_question_ids.discard(q['id'])
            form.questions.append(FormManager._update_question(q, form.id, i))
        QuestionRepository.delete_all_by_ids(list(unused_question_ids))

        return form

    @staticmethod
    def _update_question(updates: Dict[str, Any], form_id: int, index: int) -> Question:
        q_id = int(updates['id'])
        is_new = q_id == 0

        if is_new:
            question = Question(None, 0, '', 0, form_id)
            old_answers = []
        else:
            question = QuestionRepository.get_by_id(q_id)
            if not question:
                raise KeyError("Question not found")
            old_answers = AnswerRepository.get_all_by_question_id(q_id)

        question.index = index
        question.text = updates['text']
        question.set_question_type(QuestionTypeRepository.get_by_name(updates['question_type']))

        # Insert it before answers. It allows us to to get valid id
        QuestionRepository.update_or_insert(question)

        unused_answer_ids = set(a.id for a in old_answers)
        question.answers = []
        for i, a in enumerate(updates['answers']):
            unused_answer_ids.discard(a['id'])
            question.answers.append(FormManager._update_answer(a, question.id, i))
        AnswerRepository.delete_all_by_ids(list(unused_answer_ids))

        return question

    @staticmethod
    def _update_answer(updates: Dict[str, Any], q_id: int, index: int) -> Answer:
        a_id = updates['id']
        is_new = a_id == 0
        if is_new:
            answer = Answer(None, 0, '', False, False, q_id)
        else:
            answer = AnswerRepository.get_by_id(a_id)
            if not answer:
                raise KeyError("Answer not found")

        answer.index = index
        answer.text = updates['text']
        answer.is_right = updates['is_right']

        AnswerRepository.update_or_insert(answer)

        return answer
