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

    let date_args = '?date_from=' + date_from + '&date_to=' + date_to

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
                services = '<li>No information about services</li>'
            }
            let html = `
            <div class="container mt-5">
                <div class="card">
                    <img class="hotel-image" src="/static/images/resized/1920_1080/resized_1920_1080_${data.image_id}.webp" alt="Hotel image" style="max-width: 1800px; max-height: 900px;">
                    <div class="card-body">
                        <h1 class="hotel-name">${data.name}</h1>
                        <p class="hotel-location">${data.location}</p>
                        <p class="hotel-rooms">Rooms count: ${data.rooms_count}</p>
                        <ul class="hotel-services">
                            Hotel services
                            ${services}
                        </ul>
                    </div>
                </div>
            </div>
            `
            $(".hotel-info").html(html)
        },
        error: function (data) {
            alert('failed to get the hotel information')
        }
    })
    $.ajax({
        url: "/api/v1/rooms/" + hotel_id + date_args,
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
                    services = '<li>No information about services</li>'
                }
                let button = ''
                if (room.rooms_left > 0) {
                    button = `<a class="btn btn-primary" href="/bookings/create${date_args}&room_id=${room.id}&hotel_id=${hotel_id}">Choose</a>`
                } else {
                    button = `<a class="btn btn-danger disabled">No rooms available</a>`
                }

                let card = `
                <div class="card">
                    <div class="row no-gutters">
                        <div class="col-md-4">
                            <img class="card-img" src="/static/images/resized/1024_562/resized_1024_562_${room.image_id}.webp" alt="Room image" style="width: 400px; height: 200px;">
                        </div>
                        <div class="col-md-8">
                            <div class="card-body">
                                <h5 class="card-title">${room.name}</h5>
                                <p class="card-text">Description: ${room.description}</p>
                                <p class="card-text">Price: ${room.price}р per night</p>
                                <p class="card-text">Booking cost: ${room.total_cost}р за ${getDateDaysDifference(date_from, date_to)} дней</p>
                                <p class="card-text">Rooms count: ${room.quantity}</p>
                                <p class="card-text">Rooms left: ${room.rooms_left}</p>
                                <p class="card-text">
                                    Room services
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
            alert('failed to get the rooms information for this hotel')
        }
    });
})
