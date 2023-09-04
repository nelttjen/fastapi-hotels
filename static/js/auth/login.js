

$(document).ready(function() {
    $('#login-button').click(function(event) {
        event.preventDefault();

        var username = $('#username').val();
        var password = $('#password').val();

        var data = 'username=' + username + '&password=' + password;

        $.ajax({
            url: '/api/v1/auth/login/',
            method: 'POST',
            data: data,
            contentType: 'application/x-www-form-urlencoded',
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
                    case 401:
                        alert('Incorrect username or password.');
                        break
                    case 422:
                        alert('Username and password are required.');
                        break
                }
            }
        });
    });
});