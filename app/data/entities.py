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

    def set_form_type(self, form_type: FormType):
        self.form_type = form_type
        self.form_type_id = form_type.id
        return self

    def set_creator(self, creator: User):
        self.creator = creator
        self.creator_id = creator.id
        return self
