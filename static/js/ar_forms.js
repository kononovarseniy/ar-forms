'use strict';

function do_callback(func, ...args) {
    if (func)
        func.apply(this, args);
}

function toggle_class(element, className) {
    if (element.classList.contains(className))
        element.classList.remove(className)
    else
        element.classList.add(className)
}

class BarrierEvent {
    #triggered = false
    #queue = []

    do_after(func) {
        if (this.#triggered)
            func();
        else
            this.#queue.push(func);
    }

    trigger() {
        this.#triggered = true;
        for (let func of this.#queue)
            func();
    }

    get triggered() {
        return this.#triggered;
    }
}

class API {
    static query(method, args) {
        let url = new URL('/api/' + method, window.location);
        for (let [key, value] of Object.entries(args))
            url.searchParams.set(key, value.toString());

        let error_callback = null;
        let load_callback = null;

        let query = new XMLHttpRequest();
        query.open('GET', url.toString());
        query.onload = function () {
            let response;
            try {
                response = JSON.parse(query.response);
            } catch (e) {
                do_callback(error_callback, `Failed to parse server response (HTTP status: ${query.status})`);
                return;
            }
            if (response.success)
                do_callback(load_callback, response.result);
            else
                do_callback(error_callback, response.error);
        };
        query.onerror = function () {
            do_callback(error_callback, "Failed to connect to the server");
        };

        return {
            on_load: function (func) {
                load_callback = func;
                return this;
            },
            on_error: function (func) {
                error_callback = func
                return this;
            },
            send: function () {
                query.send();
            }
        };
    }

    static get_form(form_id, get_answers = false) {
        return API.query('get_form', {form_id: form_id, get_answers: get_answers});
    }

    static update_form(form, publish = false) {
        return API.query('update_form', {
            form: JSON.stringify(form),
            publish: publish
        });
    }

    static delete_form(form_id) {
        return API.query('delete_form', {form_id: form_id})
    }

    static publish_form(form_id) {
        return API.query('publish_form', {form_id: form_id})
    }

    static submit_form(form_id, answers) {
        return API.query('submit_form', {
            form_id: form_id,
            answers: JSON.stringify(answers)
        });
    }
}

class Modal {
    #positive_callback = null;
    #neutral_callback = null;
    #negative_callback = null;
    #modal

    constructor(element) {
        let scope = this;
        this.#modal = element;
        this.#modal.onclick = function (event) {
            if (event.target === element) {
                scope.hide();
                do_callback(scope.#neutral_callback);
            }
        }
    }

    on_positive(callback) {
        this.#positive_callback = callback;
        return this;
    }

    on_neutral(callback) {
        this.#neutral_callback = callback;
        return this;
    }

    on_negative(callback) {
        this.#negative_callback = callback;
        return this;
    }

    show() {
        let pos_b = this.#modal.querySelector('[name=modal-positive]'),
            neu_b = this.#modal.querySelector('[name=modal-neutral]'),
            neg_b = this.#modal.querySelector('[name=modal-negative]');

        this.#modal.style.display = 'block';

        let scope = this;
        if (pos_b) pos_b.onclick = function () {
            scope.hide();
            do_callback(scope.#positive_callback);
        };
        if (neu_b) neu_b.onclick = function () {
            scope.hide();
            do_callback(scope.#neutral_callback);
        };
        if (neg_b) neg_b.onclick = function () {
            scope.hide();
            do_callback(scope.#negative_callback);
        };
    }

    hide() {
        this.#modal.style.display = 'none';
    }
}

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

let modals_init = new BarrierEvent();

let document_loaded = new BarrierEvent();

document.addEventListener('DOMContentLoaded', () => document_loaded.trigger())


function init_menu() {
    let menu = document.getElementById('menu');
    if (menu == null) // Current page does not have a menu
        return;

    let menuLink = document.getElementById('menu-link'),
        content = document.getElementById('main'),
        layout = document.getElementById('layout');

    function toggleAll(e) {
        const active = 'active';

        toggle_class(layout, active);
        toggle_class(menu, active);
        toggle_class(menuLink, active);
    }

    menuLink.onclick = function (e) {
        e.preventDefault();
        toggleAll(e);

        content.onclick = function (e) {
            e.preventDefault();
            if (menu.classList.contains('active')) {
                toggleAll(e);
            }
            content.onclick = null;
        };
    };
}

function init_modals() {
    for (let element of document.getElementsByClassName('modal')) {
        element.modal = new Modal(element);
    }
    modals_init.trigger();
}

function init_buttons() {
    document.getElementsByName('new_form_button')
        .forEach((e) => e.onclick = onNewFormButtonClick)

    document.getElementsByName('button-delete')
        .forEach((e) => e.onclick = onDeleteButtonClick)

    document.getElementsByName('button-edit')
        .forEach((e) => e.onclick = onEditButtonClick)

    document.getElementsByName('button-publish')
        .forEach((e) => e.onclick = onPublishButtonClick)
}

function checkRegistrationForm() {
    let first = document.getElementById('password')
    let second = document.getElementById('confirm-password')
    if (first.value !== second.value) {
        let msg = document.getElementById('error-label')
        msg.textContent = 'Passwords do not match';
        return false;
    } else {
        return true
    }
}

function show_error_message(message) {
    modals_init.do_after(function () {
        let element = document.getElementById('modal-error');
        element.querySelector('[name=modal-error-text]').textContent = message;
        element.modal.show();
    });
}

function show_message(message) {
    modals_init.do_after(function () {
        let element = document.getElementById('modal-info');
        element.querySelector('[name=modal-error-text]').textContent = message;
        element.modal.show();
    });
}

function show_delete_confirmation_dialog(form_name, callback) {
    modals_init.do_after(function () {
        let element = document.getElementById('modal-confirm-delete');
        element.querySelector('[name=modal-form-name]').textContent = form_name;
        element.modal.on_positive(callback).show();
    });
}

function show_publish_confirmation_dialog(form_name, callback) {
    modals_init.do_after(function () {
        let element = document.getElementById('modal-confirm-publish');
        element.querySelector('[name=modal-form-name]').textContent = form_name;
        element.modal.on_positive(callback).show();
    });
}

function show_publish_confirmation_dialog_from_edit(callback) {
    modals_init.do_after(function () {
        let element = document.getElementById('modal-confirm-publish-from-edit');
        element.modal.on_positive(callback).show();
    });
}

function go_to_edit_form_page(form_id = 0) {
    location.href = `/edit_form?form_id=${form_id}`
}

function go_to_dashboard() {
    window.location.href = '/dashboard';
}

document_loaded.do_after(init_menu)
document_loaded.do_after(init_buttons)
document_loaded.do_after(init_modals)

function onNewFormButtonClick(event) {
    go_to_edit_form_page();
}

function onDeleteButtonClick(event) {
    let id = parseInt(event.target.getAttribute('form_id'));

    API.get_form(id)
        .on_load(delete_with_confirmation)
        .on_error(show_error_message)
        .send();

    function delete_with_confirmation(form) {
        show_delete_confirmation_dialog(form.title, do_deletion);
    }

    function do_deletion() {
        API.delete_form(id)
            .on_load(function () {
                location.reload();
            })
            .on_error(show_error_message)
            .send();
    }
}

function onEditButtonClick(event) {
    go_to_edit_form_page(parseInt(event.target.getAttribute('form_id')));
}

function onPublishButtonClick(event) {
    let id = parseInt(event.target.getAttribute('form_id'));

    API.get_form(id)
        .on_load(publish_with_confirmation)
        .on_error(show_error_message)
        .send();

    function publish_with_confirmation(form) {
        show_publish_confirmation_dialog(form.title, publish);
    }

    function publish() {
        API.publish_form(id)
            .on_load(function () {
                location.reload();
            })
            .on_error(show_error_message)
            .send();
    }
}