function check_registration_form() {let first = $('#password')
    let second = $('#confirm-password')
    if (first.val() !== second.val()) {
        let msg = $('#error-label')
        msg.text('Passwords do not match')
        msg.show()
        return false;
    } else {
        return true
    }
}