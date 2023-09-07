$(document).ready(function() {
    const url = new URL(window.location.href);
    const pathSegments = url.pathname.split("/");
    const hotel_id = parseInt(pathSegments[2])
    const queryParams = new URLSearchParams(window.location.search);

    let date_from = queryParams.get("date_from")
    let date_to = queryParams.get("date_to")
    if (date_from == null) {
        date_from = new Date().toISOString().split('T')[0]
    }
    if (date_to == null) {
        date_to = new Date().toISOString().split('T')[0]
    }

    $.ajax({
        url: "/api/v1/hotels/" + hotel_id,
        method: "GET",
        success: function(data) {
            let services = ''
            if (data.services.length > 0) {
                for (let i = 0; i < data.services.length; i++) {
                    services += `<li>${data.services[i]}</li>`
                }
            } else {
                services = '<li>Нет дополнительных услуг</li>'
            }
            let html = `
            <div class="container mt-5">
                <div class="card">
                    <img class="hotel-image" src="/static/images/resized/1920_1080/resized_1920_1080_${data.image_id}.webp" alt="Изображение отеля" style="max-width: 1800px; max-height: 900px;">
                    <div class="card-body">
                        <h1 class="hotel-name">${data.name}</h1>
                        <p class="hotel-location">${data.location}</p>
                        <p class="hotel-rooms">Всего комнат: ${data.rooms_count}</p>
                        <ul class="hotel-services">
                            ${services}
                        </ul>
                    </div>
                </div>
            </div>
            `
            $(".hotel-info").html(html)
        },
        error: function (data) {
            alert('failed to get hotel info')
        }
    })
    $.ajax({
        url: "/api/v1/rooms/" + hotel_id + '?date_from=' + date_from + '&date_to=' + date_to,
        method: "GET",
        success: function(data) {
            let cards = [];
            data.forEach(function(room) {
                let services = ''
                if (room.services.length > 0) {
                    for (let i = 0; i < room.services.length; i++) {
                        services += `<li>${room.services[i]}</li>`
                    }
                } else {
                    services = '<li>Нет дополнительных услуг</li>'
                }
                let button = ''
                if (room.rooms_left > 0) {
                    button = `<button class="btn btn-primary">Забронировать</button>`
                } else {
                    button = `<button class="btn btn-danger disabled">Нет свободных комнат</button>`
                }

                let card = `
                <div class="card">
                    <div class="row no-gutters">
                        <div class="col-md-4">
                            <img class="card-img" src="/static/images/resized/1024_562/resized_1024_562_${room.image_id}.webp" alt="Изображение комнаты" style="width: 400px; height: 200px;">
                        </div>
                        <div class="col-md-8">
                            <div class="card-body">
                                <h5 class="card-title">Название: ${room.name}</h5>
                                <p class="card-text">Описание: ${room.description}</p>
                                <p class="card-text">Цена: ${room.price}р за ночь</p>
                                <p class="card-text">Стоимость брони: ${room.total_cost}р за ${getDateDaysDifference(date_from, date_to)} дней</p>
                                <p class="card-text">Количество комнат: ${room.quantity}</p>
                                <p class="card-text">Комнат осталось: ${room.rooms_left}</p>
                                <p class="card-text">
                                    Услуги в номере
                                    <ul class="list-group">
                                        ${services}
                                    </ul>
                                </p>

                            </div>
                            <div class="card-footer">
                                ${button}
                            </div>
                        </div>
                    </div>
                </div>
                `
                cards.push(card);
            })
            $('.rooms-list').html(cards.join('<br>'))
        },
        error: function(data) {
            alert('failed to get rooms for this hotel')
        }
    });
})
