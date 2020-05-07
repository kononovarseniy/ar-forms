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
    return (
        old_form.id === 0 || new_form.id === 0 ||
        old_form.id !== new_form.id ||
        old_form.title !== new_form.title ||
        old_form.description !== new_form.description ||
        old_form.form_type !== new_form.form_type
        // TODO: compare questions
    );
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
    return (
        old_q.id === 0 || new_q === 0 ||
        old_q.id !== new_q.id ||
        old_q.text !== new_q.text ||
        old_q.type !== new_q.type
        // TODO: compare answers
    )
}

let Answer = {};
Answer.createEmpty = function () {
    return {
        id: 0,
        text: 0,
        is_right: 0,
        is_user_answer: 0
    };
};

class AnswerViewFactory {
    #types = new Map()

    registerType(typename, answerView) {
        this.#types.set(typename, answerView);
    }

    createView(typename) {
        let ctor = this.#types.get(typename);
        return new ctor();
    }
}

class QuestionView {
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

    }
}

class AnswerView {
    _element

    get element() {
        return this._element;
    }

    get edited_answers() {
        return [];
    }

    get current_answers() {
        return [];
    }

    set current_answers(value) {

    }
}

class AnswerListView extends AnswerView {

}

class AnswerRadioListView extends AnswerListView {

}

class AnswerCheckboxListView extends AnswerListView {

}

class FreeAnswerView extends AnswerView {

}

let answerViewFactory = new AnswerViewFactory();
answerViewFactory.registerType('single-variant', AnswerRadioListView);
answerViewFactory.registerType('multiple-variants', AnswerCheckboxListView);
answerViewFactory.registerType('free-answer', FreeAnswerView);

class FormView {
    #current_form;

    #title;
    #description;
    #form_type;
    #question_list;

    #question_views;

    constructor() {
        this.#title = document.getElementById('form_title');
        this.#description = document.getElementById('form_description');
        this.#form_type = document.getElementById('form_type');
        this.#question_list = document.getElementById('question-list');
    }

    _update_question_indices() {
        this.#question_views.forEach((view, i) => {
            view.question_index = i + 1;
        });
    }

    _set_fields(form) {
        this.#title.value = form.title;
        this.#description.value = form.description;
        this.#form_type.value = form.form_type;

        this.#question_list.textContent = '';
        this.#question_views = [];
        for (let q of form.questions) {
            let view = new QuestionView();
            view.current_question = q;
            view.on_delete = () => {
                let index = this.#question_views.indexOf(view);
                this.#question_views.splice(index, 1);
                view.remove();
                this._update_question_indices();
            };

            this.#question_list.append(view.element);
            this.#question_views.push(view);
        }
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


let form_view;

let on_form_init = new BarrierEvent();

function init_page() {
    form_view = new FormView();
    on_form_init.trigger();

    document.getElementById('save_button').onclick = on_save;
    document.getElementById('publish_button').onclick = on_publish;
    document.getElementById('cancel_button').onclick = on_cancel;
}

function set_current_form(form) {
    on_form_init.do_after(function () {
        form_view.current_form = form
    });
}

function load_form(form_id) {
    if (form_id === 0) {
        set_current_form(Form.createEmpty());
    } else {
        API.get_form(form_id)
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
    let form = form_view.edited_form;

    API.update_form(form, publish)
        .on_load(function (result) {
            set_current_form(result);
            do_callback(callback);
        })
        .on_error(show_error_message)
        .send();
}

function go_to_dashboard() {
    window.location.href = '/dashboard';
}

function on_save() {
    send_form_updates(false, null);
}

function on_publish() {
    show_publish_confirmation_dialog_from_edit(function () {
        send_form_updates(true, go_to_dashboard);
    });
}

function on_cancel() {
    if (!form_view.is_changed) {
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
