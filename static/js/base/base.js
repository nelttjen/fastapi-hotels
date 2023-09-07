function getExpireAccess(){
    return new Date(new Date().getTime() + 60 * 60 * 1000);
}

function getExpireRefresh() {
    return new Date(new Date().getTime() + 14 * 24 * 60 * 60 * 1000);
}

function setCookie(name, value, date) {
    document.cookie = `${name}=${value}; expires=${date.toUTCString()}; path=/;}`;
}

function getCookie(cookieName) {
    const name = cookieName + "=";
    const decodedCookie = decodeURIComponent(document.cookie);
    const cookieArray = decodedCookie.split(';');

    for(let i = 0; i < cookieArray.length; i++) {
        let cookie = cookieArray[i];
        while (cookie.charAt(0) === ' ') {
            cookie = cookie.substring(1);
        }
        if (cookie.indexOf(name) === 0) {
            return cookie.substring(name.length, cookie.length);
        }
    }

    return null;
}

function refreshToken() {
    let refresh_token = getCookie('refresh_token');
    if (!refresh_token) {
        window.location.replace('/auth/login');
        return {};
    }
    $.ajax({
        url: '/api/v1/auth/refresh',
        type: 'POST',
        contentType: 'application/json',
        data: JSON.stringify({refresh_token: refresh_token}),
        success: function(data) {
            if (data.access_token && data.refresh_token) {
                setCookie('access_token', data.access_token, getExpireAccess());
                setCookie('refresh_token', data.refresh_token, getExpireRefresh());
                setCookie('user', data.user, getExpireRefresh());
                return {'Authorization': `Bearer ${data.access_token}`}
            } else {
                window.location.replace('/auth/login');
                return {};
            }
        },
        error: function(data) {
            window.location.replace('/auth/login');
            return {};
        }
    });
}

function validateToken() {
    let access_token = getCookie('access_token');
    if (!access_token) {
        return refreshToken();
    }

    let headers = {'Authorization': `Bearer ${access_token}`}
    $.ajax({
        url: '/api/v1/auth/validate',
        type: 'POST',
        headers: headers,
        error: function(data) {
            return refreshToken();
        }
    })
    return headers;
}

function getDateDaysDifference(dateFrom, dateTo) {
    const df = new Date(dateFrom);
    const dt = new Date(dateTo);

    const differenceInMilliseconds = dt - df;

    return differenceInMilliseconds / (1000 * 60 * 60 * 24);

}
