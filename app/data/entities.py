class EntityWithId:
    def __init__(self, entity_id):
        self.id = entity_id

    def __int__(self):
        return self.id


class User(EntityWithId):
    def __init__(self, user_id, login, display_name):
        super().__init__(user_id)
        self.login = login
        self.display_name = display_name


class FormType(EntityWithId):
    def __init__(self, type_id, name):
        super().__init__(type_id)
        self.name = name


class Form(EntityWithId):
    def __init__(self, form_id, title, description, form_type, creator, creation_date, is_public):
        super().__init__(form_id)
        self.title = title
        self.description = description
        self.form_type_id = int(form_type)
        self.creator_id = int(creator)
        self.creation_date = creation_date
        self.is_public = is_public

        self.form_type = form_type if isinstance(form_type, FormType) else None
        self.creator = creation_date if isinstance(creator, User) else None
        self.questions = None

    def set_form_type(self, form_type: FormType):
        self.form_type = form_type
        self.form_type_id = form_type.id
        return self

    def set_creator(self, creator: User):
        self.creator = creator
        self.creator_id = creator.id
        return self


class QuestionType(EntityWithId):
    def __init__(self, question_type_id, name):
        super().__init__(question_type_id)
        self.name = name


class Question(EntityWithId):
    def __init__(self, question_id, index, text, question_type, form):
        super().__init__(question_id)
        self.index = index
        self.text = text
        self.question_type_id = int(question_type)
        self.form_id = int(form)

        self.question_type = question_type if isinstance(question_type, QuestionType) else None
        self.form = form if isinstance(form, Form) else None
        self.answers = None

    def set_question_type(self, question_type: QuestionType):
        self.question_type = question_type
        self.question_type_id = question_type.id
        return self

    def set_form(self, form: Form):
        self.form = form
        self.form_id = form.id
        return self


class Answer(EntityWithId):
    def __init__(self, answer_id, index, text, is_right, is_user_variant, question):
        super().__init__(answer_id)
        self.index = index
        self.text = text
        self.is_right = is_right
        self.is_user_variant = is_user_variant
        self.question_id = int(question)

        self.question = question if isinstance(question, QuestionType) else None

    def set_question(self, question: Question):
        self.question_id = question.id
        self.question = question
        return self


class Submission(EntityWithId):
    def __init__(self, submission_id, time, form, user):
        super().__init__(submission_id)
        self.time = time
        self.form_id = int(form)
        self.user_id = int(user)

        self.form = form if isinstance(form, Form) else None
        self.user = user if isinstance(user, User) else None

    def set_form(self, form: Form):
        self.form_id = form.id
        self.form = form

    def set_user(self, user: User):
        self.user_id = user.id
        self.user = user


class SubmissionAnswer:
    def __init__(self, submission, answer):
        self.submission_id = int(submission)
        self.answer_id = int(answer)

        self.submission = submission if isinstance(submission, Submission) else None
        self.answer = answer if isinstance(answer, Answer) else None

    def set_submission(self, submission: Submission):
        self.submission_id = submission.id
        self.submission = submission

    def set_answer(self, answer: Answer):
        self.answer_id = answer.id
        self.answer = answer
