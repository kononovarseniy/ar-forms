function addDocumentLoadedListener(callback) {
    if (document.readyState !== 'loading')
        callback();
    else
        document.addEventListener('DOMContentLoaded', callback)
}

function toggleClass(element, className) {
    if (element.classList.contains(className))
        element.classList.remove(className)
    else
        element.classList.add(className)
}

function initMenu() {
    let menu = document.getElementById('menu');
    if (menu == null) // This page do not have menu
        return;

    let menuLink = document.getElementById('menu-link'),
        content = document.getElementById('main'),
        layout = document.getElementById('layout');

    function toggleAll(e) {
        const active = 'active';

        toggleClass(layout, active);
        toggleClass(menu, active);
        toggleClass(menuLink, active);
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

function check_registration_form() {
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

addDocumentLoadedListener(initMenu)