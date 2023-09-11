function setData(data) {
    document.getElementById("roomName").textContent += data.room.name;
    document.getElementById("roomDescription").textContent = data.room.description;
    document.getElementById("dateFrom").textContent += data.date_from;
    document.getElementById("dateTo").textContent += data.date_to;
    document.getElementById("totalCost").textContent += data.total_cost + "р";
    document.getElementById("totalDays").textContent += data.total_days + " days";
    document.getElementById("hotelName").textContent += data.room.hotel.name;
    document.getElementById("hotelLocation").textContent += data.room.hotel.location;
    document.getElementById("hotelServices").textContent += data.room.hotel.services.join(', ');

    $('#room-image').attr('src', `/static/images/resized/1024_562/resized_1024_562_${data.room.image_id}.webp`);
    $('#hotel-image').attr('src', `/static/images/resized/1024_562/resized_1024_562_${data.room.hotel.image_id}.webp`);
}

async function fetchBookingData() {
    let hotel_id = window.location.pathname.split('/')[3];

    $.ajax({
        url: `/api/v1/bookings/my/${hotel_id}`,
        method: 'GET',
        headers: authHeaders,
        success: function(data) {
            setData(data);
        },
        error: function (data){
            window.location.href = '/bookings/my';
        }
    })
}

function deleteBooking(booking_id) {
    $.ajax({
        url: `/api/v1/bookings/my/${booking_id}`,
        method: 'DELETE',
        headers: authHeaders,
        success: function(data) {
            window.location.href = '/bookings/my';
        },
        error: function (data){
            window.location.href = '/bookings/my';
        }
    })

}

$(document).ready(async function() {
    await validateToken();
    while (!authHeaders) {
        await new Promise(resolve => {
            setTimeout(() => {
                resolve()
            }, 1000);
        })
    }
    await new Promise(resolve => {
        setTimeout(() => {
            resolve()
        }, 100);
    })
    // alert(`logged in as ${authHeaders['Authorization']}`);
    await fetchBookingData();

    $('#deleteButton').click(async function(e) {
        e.preventDefault();
        let confirmation = confirm("Are you sure you want to delete this booking?");

        if (confirmation) {
            await deleteBooking(window.location.pathname.split('/')[3]);
        } else {
        }
    })
});