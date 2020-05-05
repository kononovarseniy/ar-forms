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
        // TODO: compare answers
    );
}

let Question = {};
Question.createEmpty = function () {
    return {
        id: 0,
        index: 0,
        text: '',
        question_type: 'single-variant',
        answers: []
    };
};

let Answer = {};
Answer.createEmpty = function () {
    return {
        id: 0,
        index: 0,
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
        return this.#types.get(typename)();
    }
}

class QuestionView {
    #templateProvider
    #answerViewFactory

    #element = {
        dom: null,
        number: null,
        type: null,
        text: null,
        answers: null
    }

    #question = {
        number: 0,
        type: 'one',
        text: '',
        answers: []
    }

    constructor(templateProvider, answerViewFactory) {

    }

    async create(templateProvider, answerViewFactory) {
        let self = new QuestionView();
        self.#templateProvider = templateProvider;
        self.#answerViewFactory = answerViewFactory;
        await self.buildElement();
        return self;
    }

    async buildElement() {
        let element = await this.#templateProvider.getTemplate('question');
        let number = element.querySelector('#question-number');
        let text = element.querySelector('#question-text');
        let type = element.querySelector('#question-type');
        let answers = this.#answerViewFactory.createView();
        res.textContent = question.number;
        res.value = question.text;
        let selector = res
        selector.value = question.type;
        selector.onclick = (event) => this.onQuestionTypeSelected(event);
        this.#element = res;
    }

    get element() {
        return this.#element;
    }

    set question(value) {

    }

    get question() {
        this.#element.querySelector('#question-number')
    }

    onQuestionTypeSelected(event) {

    }
}

class AnswerView {
    _element

    get element() {
        return this._element;
    }

    get answers() {
        return [];
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

let templateProvider = new TemplateProvider();

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

    constructor() {
        this.#title = document.getElementById('form_title');
        this.#description = document.getElementById('form_description');
        this.#form_type = document.getElementById('form_type');
        this.#question_list = document.getElementById('question-list');
    }

    _set_fields(form) {
        this.#title.value = form.title;
        this.#description.value = form.description;
        this.#form_type.value = form.form_type;

        this.#question_list.textContent = '';
        for (let q of form.questions) {
            let view = new QuestionView(templateProvider, answerViewFactory);
            view.question = q;
            this.#question_list.appendChild(view);
        }
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
            questions: [] // TODO: FETCH QUESTIONS
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