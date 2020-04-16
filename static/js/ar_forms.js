function do_callback(func, ...args) {
    if (func)
        func.apply(this, args);
}

class BarrierEventQueue {
    #blocked = true
    #queue = []

    schedule(func) {
        if (!this.#blocked)
            func();
        else
            this.#queue.push(func);
    }

    unblock() {
        this.#blocked = false;
        for (let func of this.#queue)
            func();
    }
}

let modals_barrier_queue = new BarrierEventQueue();

function after_modals_init(func) {
    modals_barrier_queue.schedule(func)
}

function after_document_loaded(callback) {
    if (document.readyState !== 'loading')
        callback();
    else
        document.addEventListener('DOMContentLoaded', callback)
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

    static get_form(form_id) {
        return API.query('get_form', {form_id: form_id});
    }

    static update_form(updates) {
        return API.query('update_form', {updates: JSON.stringify(updates)});
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

function toggle_class(element, className) {
    if (element.classList.contains(className))
        element.classList.remove(className)
    else
        element.classList.add(className)
}

function init_menu() {
    let menu = document.getElementById('menu');
    if (menu == null) // This page do not have menu
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

function init_modals() {
    for (let element of document.getElementsByClassName('modal')) {
        element.modal = new Modal(element);
    }
    modals_barrier_queue.unblock();
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
    after_modals_init(function () {
        let element = document.getElementById('modal-error');
        element.querySelector('[name=modal-error-text]').textContent = message;
        element.modal.show();
    });
}

function show_message(message) {
    after_modals_init(function () {
        let element = document.getElementById('modal-info');
        element.querySelector('[name=modal-error-text]').textContent = message;
        element.modal.show();
    });
}

function show_delete_confirmation_dialog(form_name, callback) {
    after_modals_init(function () {
        let element = document.getElementById('modal-confirm-delete');
        element.querySelector('[name=modal-form-name]').textContent = form_name;
        element.modal.on_positive(callback).show();
    });
}

function show_publish_confirmation_dialog(form_name, callback) {
    after_modals_init(function () {
        let element = document.getElementById('modal-confirm-publish');
        element.querySelector('[name=modal-form-name]').textContent = form_name;
        element.modal.on_positive(callback).show();
    });
}

function show_publish_confirmation_dialog_from_edit(callback) {
    after_modals_init(function () {
        let element = document.getElementById('modal-confirm-publish-from-edit');
        element.modal.on_positive(callback).show();
    });
}

function go_to_edit_form_page(form_id = 0) {
    location.href = `/edit_form?form_id=${form_id}`
}

after_document_loaded(init_menu)
after_document_loaded(init_buttons)
after_document_loaded(init_modals)

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
        API.update_form({id: id, state: 'deleted'})
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
        API.update_form({id: id, is_public: true, state: 'modified'})
            .on_load(function () {
                location.reload();
            })
            .on_error(show_error_message)
            .send();
    }
}