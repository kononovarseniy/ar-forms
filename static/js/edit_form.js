'use strict';

let Form = {};
Form.createEmpty = function () {
    return {
        id: 0,
        title: '',
        description: '',
        form_type: 'poll',
        questions: []
    }
};
Form.isChanged = function (old_form, new_form) {
    let form_changed =
        old_form.id === 0 || new_form.id === 0 ||
        old_form.id !== new_form.id ||
        old_form.title !== new_form.title ||
        old_form.description !== new_form.description ||
        old_form.form_type !== new_form.form_type;
    if (form_changed)
        return true;
    if (old_form.questions.length !== new_form.questions.length)
        return true;
    for (let i = 0; i < old_form.questions.length; i++)
        if (Question.isChanged(old_form.questions[i], new_form.questions[i]))
            return true;
    return false;
}

let Question = {};
Question.createEmpty = function () {
    return {
        id: 0,
        text: '',
        question_type: 'single-variant',
        answers: []
    };
};
Question.isChanged = function (old_q, new_q) {
    let question_changed =
        old_q.id === 0 || new_q.id === 0 ||
        old_q.id !== new_q.id ||
        old_q.text !== new_q.text ||
        old_q.question_type !== new_q.question_type;
    if (question_changed)
        return true;
    if (old_q.answers.length !== new_q.answers.length)
        return true;
    for (let i = 0; i < old_q.answers.length; i++)
        if (Answer.isChanged(old_q.answers[i], new_q.answers[i]))
            return true;
    return false;
}

let Answer = {};
Answer.createEmpty = function () {
    return {
        id: 0,
        text: '',
        is_right: false
    };
};
Answer.isChanged = function (old_a, new_a) {
    return (
        old_a.id === 0 || new_a.id === 0 ||
        old_a.id !== new_a.id ||
        old_a.text !== new_a.text ||
        old_a.is_right !== new_a.is_right
    );
}

class QuestionEditor {
    #element;
    #answer_view;
    #current_question;
    #question_index;
    on_delete;

    constructor() {
        let template = document.getElementById('question-template')
        let container = template.content.firstElementChild.cloneNode(true);
        this.#element = {
            container: container,
            index: container.querySelector('#question-index'),
            text: container.querySelector('#question-text'),
            question_type: container.querySelector('#question-type'),
            answers: container.querySelector('#answers-container'),
            delete_button: container.querySelector('#delete-button')
        };
        this.#element.delete_button.onclick = () => this.on_delete();
        this.#element.question_type.onclick = (event) => this.onQuestionTypeSelected(event);
    }

    get element() {
        return this.#element.container;
    }

    remove() {
        this.#element.container.remove();
    }

    get question_index() {
        return this.#question_index;
    }

    set question_index(index) {
        this.#question_index = index;
        this.#element.index.textContent = index;
    }

    get current_question() {
        return this.#current_question;
    }

    set current_question(question) {
        this.#current_question = question;

        this.#element.text.value = question.text;
        this.#element.question_type.value = question.question_type;
        this.#element.answers.textContent = '';

        this.#answer_view = answerViewFactory.createView(question.question_type);
        this.#answer_view.current_answers = question.answers;
        this.#element.answers.append(this.#answer_view.element);
    }

    get edited_question() {
        return {
            id: this.#current_question.id,
            text: this.#element.text.value,
            question_type: this.#element.question_type.value,
            answers: this.#answer_view.edited_answers
        }
    }

    onQuestionTypeSelected(event) {
        let question = this.edited_question;
        this.#element.answers.textContent = '';
        this.#answer_view = answerViewFactory.createView(question.question_type);
        this.#answer_view.current_answers = question.answers;
        this.#element.answers.append(this.#answer_view.element);
    }
}

class AnswerVariantEditor {
    #element
    #current_answer
    on_delete

    get element() {
        return this.#element.container;
    }

    remove() {
        this.#element.container.remove();
    }

    constructor(template) {
        let container = template.cloneNode(true);
        this.#element = {
            container: container,
            check: container.querySelector("#answer-is-right"),
            text: container.querySelector("#answer-text"),
            delete_button: container.querySelector("#delete-answer-button")
        }
        this.#element.delete_button.onclick = () => this.on_delete();
    }

    get current_answer() {
        return this.#current_answer;
    }

    set current_answer(answer) {
        this.#current_answer = answer;
        this.#element.check.checked = answer.is_right;
        this.#element.text.value = answer.text;
    }

    get edited_answer() {
        return {
            id: this.#current_answer.id,
            text: this.#element.text.value,
            is_right: this.#element.check.checked
        };
    }
}

class AnswerListEditor {
    #element
    #answer_template
    #current_answers
    #answer_views

    get element() {
        return this.#element.container;
    }

    constructor(answer_template) {
        this.#answer_template = answer_template;

        let template = document.getElementById('answer-list-template')
        let container = template.content.firstElementChild.cloneNode(true);
        this.#element = {
            container: container,
            list: container.querySelector("#answer-list"),
            add_button: container.querySelector("#add-answer-button")
        }
        this.#element.add_button.onclick = () => this._on_add_click();
    }

    get current_answers() {
        return this.#current_answers;
    }

    set current_answers(answers) {
        if (answers.length === 0)
            answers = [Answer.createEmpty()];
        this.#current_answers = answers;

        this.#element.list.textContent = '';
        this.#answer_views = [];
        answers.forEach((a) => this._add_answer(a));
    }

    get edited_answers() {
        return this.#answer_views.map((a) => a.edited_answer);
    }

    _add_answer(answer) {
        let view = new AnswerVariantEditor(this.#answer_template);
        view.current_answer = answer;
        view.on_delete = () => this._on_delete_answer(view);
        this.#answer_views.push(view);
        this.#element.list.append(view.element);
    }

    _on_add_click() {
        this._add_answer(Answer.createEmpty());
    }

    _on_delete_answer(view) {
        let index = this.#answer_views.indexOf(view);
        this.#answer_views.splice(index, 1);
        view.remove();
    }
}

let answer_radio_list_id_counter = 0;

class AnswerRadioListEditor extends AnswerListEditor {
    constructor() {
        let template = document.getElementById('answer-radio-template')
            .content.firstElementChild.cloneNode(true);

        template.querySelector("#answer-is-right").name += answer_radio_list_id_counter++;
        super(template);
    }
}

class AnswerCheckboxListEditor extends AnswerListEditor {
    constructor() {
        let template = document.getElementById('answer-checkbox-template')
            .content.firstElementChild.cloneNode(true);
        super(template);
    }
}

class FreeAnswerEditor {
    #element

    get element() {
        return this.#element.container;
    }

    constructor() {
        let template = document.getElementById('free-answer-template')
        let container = template.content.firstElementChild.cloneNode(true);
        this.#element = {
            container: container
        }
    }

    get current_answers() {
        return [];
    }

    set current_answers(answers) {
    }

    get edited_answers() {
        return [];
    }
}

let answerViewFactory = new AnswerViewFactory();
answerViewFactory.registerType('single-variant', AnswerRadioListEditor);
answerViewFactory.registerType('multiple-variants', AnswerCheckboxListEditor);
answerViewFactory.registerType('free-answer', FreeAnswerEditor);

class FormEditor {
    #current_form;

    #title;
    #description;
    #form_type;
    #question_list;
    #add_question_button

    #question_views;

    constructor() {
        this.#title = document.getElementById('form_title');
        this.#description = document.getElementById('form_description');
        this.#form_type = document.getElementById('form_type');
        this.#question_list = document.getElementById('question-list');
        this.#add_question_button = document.getElementById('add_question_button');
        this.#add_question_button.onclick = () => this._on_add_question_click();
    }

    _update_question_indices() {
        this.#question_views.forEach((view, i) => {
            view.question_index = i + 1;
        });
    }

    _on_delete_question(view) {
        let index = this.#question_views.indexOf(view);
        this.#question_views.splice(index, 1);
        view.remove();
        this._update_question_indices();
    }

    _add_question(question) {
        let view = new QuestionEditor();
        view.current_question = question;
        view.on_delete = () => this._on_delete_question(view);

        this.#question_list.append(view.element);
        this.#question_views.push(view);
    }

    _set_fields(form) {
        this.#title.value = form.title;
        this.#description.value = form.description;
        this.#form_type.value = form.form_type;

        this.#question_list.textContent = '';
        this.#question_views = [];
        form.questions.forEach((q) => this._add_question(q));
        this._update_question_indices();
    }

    _on_add_question_click() {
        this._add_question(Question.createEmpty());
        this._update_question_indices();
    }

    get current_form() {
        return this.#current_form;
    }

    set current_form(form) {
        this.#current_form = form;
        this._set_fields(form);
    }

    get edited_form() {
        return {
            id: this.#current_form.id,
            title: this.#title.value,
            description: this.#description.value,
            form_type: this.#form_type.value,
            questions: this.#question_views.map((q) => q.edited_question)
        };
    }

    get is_changed() {
        return Form.isChanged(this.current_form, this.edited_form);
    }
}


let form_editor;

let on_form_init = new BarrierEvent();

function init_page() {
    form_editor = new FormEditor();
    on_form_init.trigger();

    document.getElementById('save_button').onclick = on_save;
    document.getElementById('publish_button').onclick = on_publish;
    document.getElementById('cancel_button').onclick = on_cancel;
}

function set_current_form(form) {
    on_form_init.do_after(function () {
        form_editor.current_form = form
    });
}

function load_form(form_id) {
    if (form_id === 0) {
        set_current_form(Form.createEmpty());
    } else {
        API.get_form(form_id, true)
            .on_load(set_current_form)
            .on_error(show_error_message)
            .send();
    }
}

function get_form_id() {
    let args = new URLSearchParams(window.location.search);
    let form_id = parseInt(args.get('form_id'));
    if (isNaN(form_id) || form_id < 0)
        return 0;
    return form_id;
}

load_form(get_form_id());

function send_form_updates(publish, callback) {
    let form = form_editor.edited_form;

    API.update_form(form, publish)
        .on_load(function (result) {
            set_current_form(result);
            do_callback(callback);
        })
        .on_error(show_error_message)
        .send();
}

function on_save() {
    send_form_updates(false, function () {
        show_snackbar("Changes saved successfully")
    });
}

function on_publish() {
    show_publish_confirmation_dialog_from_edit(function () {
        send_form_updates(true, go_to_dashboard);
    });
}

function on_cancel() {
    if (!form_editor.is_changed) {
        go_to_dashboard();
        return;
    }

    document.getElementById('modal-confirm-exit').modal
        .on_positive(function () {
            send_form_updates(false, go_to_dashboard);
        })
        .on_negative(go_to_dashboard)
        .show();
}

document_loaded.do_after(init_page);
