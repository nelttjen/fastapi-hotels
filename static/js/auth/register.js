$(document).ready(function() {
    $('#register-button').click(function(event) {
        event.preventDefault();

        var username = $('#username').val();
        var email = $('#email').val();
        var password = $('#password').val();
        var password2 = $('#confirm_password').val();

        if (password!== password2) {
            alert('Passwords do not match.');
            return;
        }

        data = {
            username: username,
            email: email,
            password: password
        }

        $.ajax({
            url: '/api/v1/auth/register/',
            method: 'POST',
            data: JSON.stringify(data),
            contentType: 'application/json',
            success: function(response) {
                if (response.access_token && response.refresh_token) {
                    setCookie('access_token', response.access_token, getExpireAccess());
                    setCookie('refresh_token', response.refresh_token, getExpireRefresh());
                    setCookie('user', JSON.stringify(response.user), getExpireRefresh())


                    alert('Login successful! Access token and refresh token set as cookies.');
                } else {
                    alert('Server did not return access token.');
                }
            },
            error: function(error) {
                switch (error.status) {
                    case 400:
                        alert(error.detail)
                        break;
                    case 401:
                        alert('Incorrect username or password.');
                        break;
                    case 409:
                        alert('Username is taken.');
                        break;
                    case 422:
                        alert('Username, email and password are required.');
                        break;
                }
            }
        });
    });
});
