'use strict';

class QuestionView {
    #element;
    #answer_view;
    #current_question;
    #question_index;

    constructor() {
        let template = document.getElementById('question-template')
        let container = template.content.firstElementChild.cloneNode(true);
        this.#element = {
            container: container,
            index: container.querySelector('#question-index'),
            text: container.querySelector('#question-text'),
            answers: container.querySelector('#answers-container'),
            header: container.querySelector('.card-header')
        };
    }

    get element() {
        return this.#element.container;
    }

    get question_index() {
        return this.#question_index;
    }

    set question_index(index) {
        this.#question_index = index;
        this.#element.index.textContent = index;
    }

    set current_question(question) {
        this.#current_question = question;

        this.#element.text.textContent = question.text;
        this.#element.answers.textContent = '';
        this.#element.header.classList.add('question-type-' + question.question_type);

        this.#answer_view = answerViewFactory.createView(question.question_type);
        this.#answer_view.current_answers = question.answers;
        this.#element.answers.append(this.#answer_view.element);
    }

    get selected_answers() {
        return this.#answer_view.selected_answers;
    }
}

class AnswerVariantView {
    #element
    #current_answer

    get element() {
        return this.#element.container;
    }

    constructor(template) {
        let container = template.cloneNode(true);
        this.#element = {
            container: container,
            check: container.querySelector("#answer-is-right"),
            text: container.querySelector("#answer-text")
        }
    }

    get current_answer() {
        return this.#current_answer;
    }

    set current_answer(answer) {
        this.#current_answer = answer;
        this.#element.check.checked = answer.is_right;
        this.#element.text.textContent = answer.text;
    }

    get is_checked() {
        return this.#element.check.checked
    }
}

class AnswerListView {
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
        }
    }

    set current_answers(answers) {
        this.#current_answers = answers;

        this.#element.container.textContent = '';
        this.#answer_views = [];
        answers.forEach((a) => this._add_answer(a));
    }

    _add_answer(answer) {
        let view = new AnswerVariantView(this.#answer_template);
        view.current_answer = answer;
        this.#answer_views.push(view);
        this.#element.container.append(view.element);
    }

    get selected_answers() {
        return this.#answer_views.filter(v => v.is_checked).map(v => v.current_answer);
    }
}

let answer_radio_list_id_counter = 0;

class AnswerRadioListView extends AnswerListView {
    constructor() {
        let template = document.getElementById('answer-radio-template')
            .content.firstElementChild.cloneNode(true);

        template.querySelector("#answer-is-right").name += answer_radio_list_id_counter++;
        super(template);
    }
}

class AnswerCheckboxListView extends AnswerListView {
    constructor() {
        let template = document.getElementById('answer-checkbox-template')
            .content.firstElementChild.cloneNode(true);
        super(template);
    }
}

class FreeAnswerView {
    #element

    get element() {
        return this.#element.container;
    }

    constructor() {
        let template = document.getElementById('free-answer-template')
        let container = template.content.firstElementChild.cloneNode(true);
        this.#element = {
            container: container,
            text: container.querySelector('#free-answer-text')
        }
    }

    set current_answers(answers) {
    }

    get selected_answers() {
        return [{
            id: 0,
            text: this.#element.text.value,
            is_right: false,
            is_user_answer: true
        }];
    }
}

let answerViewFactory = new AnswerViewFactory();
answerViewFactory.registerType('single-variant', AnswerRadioListView);
answerViewFactory.registerType('multiple-variants', AnswerCheckboxListView);
answerViewFactory.registerType('free-answer', FreeAnswerView);

class FormView {
    #current_form;

    #title;
    #description;
    #question_list;

    #question_views;

    constructor() {
        this.#title = document.getElementById('form_title');
        this.#description = document.getElementById('form_description');
        this.#question_list = document.getElementById('question-list');
    }

    _update_question_indices() {
        this.#question_views.forEach((view, i) => {
            view.question_index = i + 1;
        });
    }

    _add_question(question) {
        let view = new QuestionView();
        view.current_question = question;

        this.#question_list.append(view.element);
        this.#question_views.push(view);
    }

    _set_fields(form) {
        this.#title.textContent = form.title;
        this.#description.textContent = form.description;

        this.#question_list.textContent = '';
        this.#question_views = [];
        form.questions.forEach((q) => this._add_question(q));
        this._update_question_indices();
    }

    get current_form() {
        return this.#current_form;
    }

    set current_form(form) {
        this.#current_form = form;
        this._set_fields(form);
    }

    get selected_answers() {
        return this.#question_views.map(v => v.selected_answers);
    }
}

let form_view;

let on_form_init = new BarrierEvent();

function init_page() {
    form_view = new FormView();
    on_form_init.trigger();

    document.getElementById('send_button').onclick = on_send;
    document.getElementById('cancel_button').onclick = on_cancel;
}

function set_current_form(form) {
    on_form_init.do_after(function () {
        form_view.current_form = form
    });
}

function load_form(form_id) {
    if (form_id === 0) {
        show_error_message("No such form")
    } else {
        API.get_form(form_id, false)
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

function submit_form() {
    let answers = form_view.selected_answers.map(arr => arr.map(a => a.id === 0 ? a.text : a.id));

    API.submit_form(form_view.current_form.id, answers)
        .on_load(go_to_results)
        .on_error(show_error_message)
        .send();
}

function on_send() {
    submit_form();
}

function on_cancel() {
    document.getElementById('modal-confirm-exit').modal
        .on_positive(submit_form)
        .on_negative(go_to_dashboard)
        .show();
}

document_loaded.do_after(init_page);
