$(document).ready(function() {
    $("#recovery-button").click(function (e) {
        e.preventDefault();
        let code = $('#code').val();
        let password = $('#password').val();
        let confirm_password = $('#confirm_password').val();

        if (password !== confirm_password) {
            alert('Passwords do not match');
            return false;
        }

        $.ajax({
            url: '/api/v1/auth/recovery',
            type: 'PUT',
            data: JSON.stringify({code: code, new_password: password}),
            contentType: 'application/json',
            success: function (data) {
                let form = $('.recovery-content');
                form.html(`

                <p>Password successfully changed. Now you can log in with the new password.</p>
                <a href="/auth/login" class="btn btn-primary">Log in</a>

                `);
            },
            error: function (data) {
                alert(data.responseJSON.detail);
            }
        })
    })
});
