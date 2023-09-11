let pydanticErrors = undefined;
let tomorrow = undefined;
let day2fw = undefined;

let defaultQueryDate = undefined;
let authHeaders = {};

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

async function refreshToken() {
    let refresh_token = getCookie('refresh_token');
    if (!refresh_token) {
        window.location.replace('/auth/login');
    }
    $.ajax({
        url: '/api/v1/auth/refresh',
        type: 'POST',
        contentType: 'application/json',
        data: JSON.stringify({refresh_token: refresh_token}),
        success: async function(data) {
            if (data.access_token && data.refresh_token) {
                setCookie('access_token', data.access_token, getExpireAccess());
                setCookie('refresh_token', data.refresh_token, getExpireRefresh());
                setCookie('user', JSON.stringify(data.user), getExpireRefresh());
                authHeaders = {'Authorization': `Bearer ${data.access_token}`}
            } else {
                window.location.replace('/auth/login');
            }
        },
        error: async function(data) {
            window.location.replace('/auth/login');
        }
    });
}

async function validateToken() {
    let access_token = getCookie('access_token');
    if (!access_token) {
        return await refreshToken();
    }

    authHeaders = {'Authorization': `Bearer ${access_token}`}
    $.ajax({
        url: '/api/v1/auth/validate',
        type: 'POST',
        headers: authHeaders,
        error: async function(data) {
            return await refreshToken();
        }
    })
}

function getDateDaysDifference(dateFrom, dateTo) {
    const df = new Date(dateFrom);
    const dt = new Date(dateTo);

    const differenceInMilliseconds = dt - df;

    return differenceInMilliseconds / (1000 * 60 * 60 * 24);

}


function formatHeader() {
    const $userProfileList = $('.user-profile');
    const userCookie = getCookie('user');

    let user = undefined;
    try {
        user = JSON.parse(userCookie);
    } catch (e) {}

    if (user) {

        $userProfileList.html(`
            <li class="nav-item">
                <a class="nav-link" href="/bookings/my">
                    <img src="/static/images/default/avatar.png" width="29" height="29" alt="avt" style="margin-right: 8px;">
                    <span>${user.username}</span>
                </a>
            </li>
            <li class="nav-item">
                <a class="nav-link" href="/auth/logout">Log out</a>
            </li>
        `);

    } else {
        $userProfileList.html(`
        <li class="nav-item"><a class="nav-link" href="/auth/login">Log in</a></li>
        <li class="nav-item"><a class="nav-link" href="/auth/register">Register</a></li>
        `)
    }
}

function displayPydanticErrors(errors) {
    if (!pydanticErrors) {
        return;
    }

    let lis = ``
    errors.forEach(function(error) {
        lis += `
        <li class="list-group-item" style="color: red;">
        <p>${error.type}:</p> <p>${error.msg}</p> <p>(location: ${error.loc.join(' - ')})</p>
        </li>
        `
    });
    pydanticErrors.empty();
    pydanticErrors.html(lis);
}

$(document).ready(function() {
    formatHeader();

    pydanticErrors = $('.pydantic-errors');

    tomorrow = new Date();
    day2fw = new Date();

    tomorrow.setDate(tomorrow.getDate() + 1);
    day2fw.setDate(day2fw.getDate() + 2);

    defaultQueryDate = "?date_from=";
    defaultQueryDate += tomorrow.toJSON().split('T')[0];
    defaultQueryDate += "&date_to=";
    defaultQueryDate += day2fw.toJSON().split('T')[0];
});
