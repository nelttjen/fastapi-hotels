$(document).ready(function() {
    let code = $('#code').val();
    $.ajax({
        url: '/api/v1/auth/activate',
        type: 'PUT',
        data: JSON.stringify({code: code}),
        contentType: 'application/json',
        success: function(data) {
            $('.activation-result').html(`
                <h1>Activation successful! Now you can log in into your account.</h1>
                <a href="/auth/login" class="btn btn-primary">Log in</a>
            `);
        },
        error: function(data) {
            $('.activation-result').html(`
                <h1>${data.responseJSON.detail}</h1>
                <a href="/auth/login" class="btn btn-primary">Log in</a>
            `);
        }
    });
})
