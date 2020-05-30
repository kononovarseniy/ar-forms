import csv
import io
import zipfile
from datetime import datetime
from typing import Iterator, Tuple, List

from data import SubmissionRepository, QuestionRepository, SubmissionAnswerRepository, AnswerRepository
from data.entities import User, Form, Submission, Question
from model import FormManager


class _SubmissionHandler:
    def __init__(self, filename: str):
        self.filename = filename

    def flush(self, archive: zipfile.ZipFile) -> None:
        with archive.open(self.filename, 'w') as file:
            self._write_to(file)

    def _write_to(self, file):
        pass


class _CsvSubmissionHandler(_SubmissionHandler):
    def __init__(self, filename: str):
        super().__init__(filename)
        self.rows = []

    def handle_submission(self, s: Submission) -> None:
        pass

    def _write_to(self, file) -> None:
        with io.TextIOWrapper(file) as text_writer:
            writer = csv.writer(text_writer)
            writer.writerows(self.rows)


class _SubmissionsFileHandler(_CsvSubmissionHandler):
    def __init__(self, filename: str):
        super().__init__(filename)
        self.rows.append(['submission_id', 'login', 'display_name', 'time'])

    def handle_submission(self, s: Submission) -> None:
        self.rows.append([s.id, s.user.login, s.user.display_name, s.time])


class _SingleVariantQuestionWriter(_CsvSubmissionHandler):
    def __init__(self, filename: str, question: Question):
        super().__init__(filename)
        self.question = question
        self.rows.append(['submission_id', 'answer'])

    def handle_submission(self, s: Submission) -> None:
        self.rows.append([s.id, s.answers[self.question.index][0].index + 1])


class _MultipleVariantsQuestionWriter(_CsvSubmissionHandler):
    def __init__(self, filename: str, question: Question):
        super().__init__(filename)
        self.question = question
        self.rows.append(['submission_id'] + [a.text for a in question.answers])

    def handle_submission(self, s: Submission) -> None:
        selected = set(a.id for a in s.answers[self.question.index])
        self.rows.append([s.id] + [1 if a.id in selected else 0 for a in self.question.answers])


class _FreeAnswerVariantQuestionWriter(_CsvSubmissionHandler):
    def __init__(self, filename: str, question: Question):
        super().__init__(filename)
        self.question = question
        self.rows.append(['submission_id', 'answer'])

    def handle_submission(self, s: Submission) -> None:
        self.rows.append([s.id, s.answers[self.question.index][0].text])


def create_handler_for_question(filename: str, question: Question) -> _CsvSubmissionHandler:
    type_name = question.question_type.name
    if type_name == 'single-variant':
        return _SingleVariantQuestionWriter(filename, question)
    elif type_name == 'multiple-variants':
        return _MultipleVariantsQuestionWriter(filename, question)
    elif type_name == 'free-answer':
        return _FreeAnswerVariantQuestionWriter(filename, question)


class FormStatisticsManager:
    @staticmethod
    def create_zip_file(user: User, form_id: int, file) -> str:
        form = FormManager.get_form_by_id(user, form_id, True)
        if not FormManager.is_owner(user, form):
            raise PermissionError("You are not the owner of this form")

        handlers = [
            create_handler_for_question(f'{q.index + 1}.csv', q)
            for q in form.questions
        ]
        handlers.append(_SubmissionsFileHandler('submissions.csv'))
        submissions, questions = FormStatisticsManager.get_submissions_by_form(form)
        for s in submissions:
            for h in handlers:
                h.handle_submission(s)

        with zipfile.ZipFile(file, 'w') as archive:
            for h in handlers:
                h.flush(archive)
            FormStatisticsManager.write_form_file(archive, form)

        return f'{form.id}_{form.title}_{datetime.now():%Y%m%d-%H%M%S}.zip'

    @staticmethod
    def write_form_file(archive, form):
        with io.TextIOWrapper(archive.open('form.txt', 'w')) as f:
            f.write(f'Form ID: {form.id}\n')
            f.write(f'Title: {form.title}\n')
            f.write(f'Description: {form.description}\n\n')
            for q in form.questions:
                f.write(f'{q.index + 1}) {q.text}\n')
                type_name = q.question_type.name
                f.write(f'Type: {type_name}\n')
                if type_name == 'single-variant':
                    for a in q.answers:
                        f.write(f'\t{a.index + 1}) ({"X" if a.is_right else " "}) {a.text}\n')
                elif type_name == 'multiple-variants':
                    for a in q.answers:
                        f.write(f'\t{a.index + 1}) [{"X" if a.is_right else " "}] {a.text}\n')
                f.write('\n')

    @staticmethod
    def get_submissions_by_form(form: Form) -> Tuple[Iterator[Submission], List[Question]]:
        submissions = SubmissionRepository.get_by_form_join_users(form)
        questions = list(QuestionRepository.get_all_by_form_id(form.id))
        questions.sort(key=lambda q: q.index)
        for question in questions:
            question.answers = list(AnswerRepository.get_all_by_question_id(question.id))
            question.answers.sort(key=lambda v: v.index)

        def iterate_submissions():
            id_index_map = {q.id: i for i, q in enumerate(questions)}
            for s in submissions:
                chosen_variants_by_question = list([] for _ in range(len(questions)))
                for a in SubmissionAnswerRepository.get_by_submission_join_answers(s):
                    index = id_index_map.get(a.answer.question_id)
                    if index is None:
                        raise KeyError("Corrupted database")
                    chosen_variants_by_question[index].append(a.answer)

                for variants in chosen_variants_by_question:
                    variants.sort(key=lambda variant: variant.index)
                s.answers = chosen_variants_by_question
                yield s

        return iterate_submissions(), questions
