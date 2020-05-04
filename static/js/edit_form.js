let edit_form_barrier_queue = new BarrierEventQueue();

class TemplateProvider {
    #map = new Map()

    async getTemplate(name) {
        if (this.#map.has(name))
            return this.#map.get(name).cloneNode(true);

        let response = await fetch(`/templates/${name}.html`);
        if (!response.ok)
            throw new Error(`Failed to load template. Status: ${response.status}`);

        let template = await response.text();
        let dom = new DOMParser().parseFromString(template, "text/html");
        this.#map.set(name, dom);

        return dom.cloneNode(true);
    }
}

class AnswerViewFactory {
    registerType(typename, answerView) {

    }

    getTypes() {

    }

    createView(typename) {

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
        question = new Question()
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
answerViewFactory.registerType('one', AnswerRadioListView);
answerViewFactory.registerType('many', AnswerCheckboxListView);
answerViewFactory.registerType('free', FreeAnswerView);

function after_edit_form_init(func) {
    edit_form_barrier_queue.schedule(func)
}

let currentForm = empty_form();
let title = null,
    description = null,
    form_type = null,
    question_list = null;

function init_edit_form() {
    title = document.getElementById('form_title');
    description = document.getElementById('form_description');
    form_type = document.getElementById('form_type');
    question_list = document.getElementById('question-list');

    document.getElementById('save_button').onclick = onSave;
    document.getElementById('publish_button').onclick = onPublish;
    document.getElementById('cancel_button').onclick = onCancel;

    edit_form_barrier_queue.unblock();
}

function fill_fields_with_current_values() {
    title.value = currentForm.title;
    description.value = currentForm.description;
    form_type.value = currentForm.form_type;
    question_list.textContent = '';
    for (let q of currentForm.questions) {
        let view = new QuestionView(templateProvider, answerViewFactory);
        view.question = q;
        question_list.appendChild(view);
    }
}

function is_changed() {
    return currentForm.id === 0 ||
        currentForm.title !== title.value ||
        currentForm.description !== description.value ||
        currentForm.form_type !== form_type.value;
}

function set_current_form(form) {
    currentForm = form;

    after_edit_form_init(fill_fields_with_current_values);
}

function send_form_updates(publish, callback) {
    let form = {
        id: currentForm.id,
        title: title.value,
        description: description.value,
        form_type: form_type.value,
        questions: []
    };

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

function onSave() {
    send_form_updates(false, null);
}

function onPublish() {
    show_publish_confirmation_dialog_from_edit(function () {
        send_form_updates(true, go_to_dashboard);
    });
}

function onCancel() {
    if (!is_changed()) {
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

function empty_form() {
    return {
        id: 0,
        title: '',
        description: '',
        form_type: 'poll',
        questions: []
    }
}

function load_form(form_id) {
    if (form_id === 0) {
        set_current_form(empty_form());
        return;
    }

    API.get_form(form_id)
        .on_load(set_current_form)
        .on_error(show_error_message)
        .send();
}

function get_form_id() {
    let args = new URLSearchParams(window.location.search);
    let form_id = parseInt(args.get('form_id'));
    if (isNaN(form_id) || form_id < 0)
        return 0;
    return form_id;
}


load_form(get_form_id());

after_document_loaded(init_edit_form);
