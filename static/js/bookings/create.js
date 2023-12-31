$(document).ready(async function() {
    await validateToken();
    const queryParams = new URLSearchParams(window.location.search);

    let date_from = queryParams.get("date_from")
    let date_to = queryParams.get("date_to")
    let roomId = queryParams.get("room_id")
    let hotelId = queryParams.get("hotel_id")

    let tomorrow = new Date()
    let day2fw = new Date()
    tomorrow.setDate(tomorrow.getDate() + 1);
    day2fw.setDate(day2fw.getDate() + 2);
    $('#startDate').prop('min', function(){
        return tomorrow.toJSON().split('T')[0];
    });
    $('#endDate').prop('min', function(){
        return day2fw.toJSON().split('T')[0];
    });
    if (date_from) {
        $('#startDate').val(date_from);
    }
    if (date_to) {
        $('#endDate').val(date_to);
    }

    let queryDate = "";
    queryDate += "?date_from=";
    queryDate += date_from ? date_from : tomorrow.toJSON().split('T')[0];
    queryDate += "&date_to=";
    queryDate += date_to ? date_to : day2fw.toJSON().split('T')[0];

    $.ajax({
        method: "GET",
        url: `/api/v1/rooms/${hotelId}/room/${roomId}` + queryDate,
        success: function(data) {
            let servicesHtml = '';

            if (data.services.length > 0) {
                servicesHtml = `
                    <ul class="list-group">
                        ${data.services.map(service => `<li class="list-group-item">${service}</li>`).join('')}
                    </ul>
                `;
            } else {
                servicesHtml = '<p>No information about services</p>';
            }

            $('.room-info').html(`
                <div class="card">
                    <img class="card-img-top" src="/static/images/resized/1024_562/resized_1024_562_${data.image_id}.webp" alt="Room image" style="width: 100%;">
                    <div class="card-body">
                        <h2 class="card-title">${data.name}</h2>
                        <p class="card-text">${data.description}</p>
                        <ul class="list-group list-group-flush">
                            <li class="list-group-item">Price: ${data.price}р per night</li>
                            <li class="list-group-item">Booking cost: ${data.total_cost}р за ${getDateDaysDifference(date_from, date_to)} дней</li>
                            <li class="list-group-item">Rooms count: ${data.quantity}</li>
                            <li class="list-group-item">Rooms left: ${data.rooms_left}</li>
                        </ul>
                        <h3 class="mt-3">Room services</h3>
                        ${servicesHtml}
                    </div>
                </div>
            `);
        },
        error: function(data) {
            alert("Error getting information about the room: " + data.responseJSON.detail);
        }
    });
    $('#create-booking-button').click(function(e) {
        e.preventDefault();
        let date_from = $('#startDate').val();
        let date_to = $('#endDate').val();
        let roomId = $('#room_id').val();

        let payload = {
            date_from: date_from,
            date_to: date_to,
            room_id: roomId,
        };
        $.ajax({
            method: "POST",
            url: `/api/v1/bookings/create`,
            data: JSON.stringify(payload),
            contentType: "application/json",
            headers: authHeaders,
            success: function(data) {
                let form = $('.create-booking-container');
                form.html(`
                <h3 style="color: green;">You have successfully booked this room from ${date_from} to ${date_to}</h3>
                <a href="/bookings/my" class="btn btn-primary">Go to my bookings</a>
                `)
            },
            error: function(data) {
                if (data.status === 422) {
                    displayPydanticErrors(data.responseJSON.detail);
                } else {
                    let form = $('.create-booking-container');
                    form.html(`
                    <h3 style="color: red;">${data.responseJSON.detail}</h3>
                    <a href="/hotels/${hotelId}/rooms${queryDate}" class="btn btn-primary">Go back</a>
                    `)
                }
            }
        });
    })
});
