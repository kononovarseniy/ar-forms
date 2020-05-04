let edit_form_barrier_queue = new BarrierEventQueue();

function after_edit_form_init(func) {
    edit_form_barrier_queue.schedule(func)
}

let currentForm = empty_form();
let title = null,
    description = null,
    form_type = null;

function init_edit_form() {
    title = document.getElementById('form_title');
    description = document.getElementById('form_description');
    form_type = document.getElementById('form_type');

    document.getElementById('save_button').onclick = onSave;
    document.getElementById('publish_button').onclick = onPublish;
    document.getElementById('cancel_button').onclick = onCancel;

    edit_form_barrier_queue.unblock();
}

function fill_fields_with_current_values() {
    title.value = currentForm.title;
    description.value = currentForm.description;
    form_type.value = currentForm.form_type;
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
        title: title.value,
        description: description.value,
        form_type: form_type.value,
        is_public: publish
    };
    if (currentForm.id !== 0)
        form.id = currentForm.id

    API.update_form(form)
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
        'id': 0,
        'title': '',
        'description': '',
        'form_type': 'poll'
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