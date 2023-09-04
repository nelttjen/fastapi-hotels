$(document).ready(function() {
    $("#search-button").click(function(event) {
        event.preventDefault();

        var title = $("#title").val();
        var startDate = $("#startDate").val();
        var endDate = $("#endDate").val();

        var apiUrl = "/api/v1/hotels/search/" + encodeURIComponent(title);

        // Отправляем AJAX-запрос
        $.ajax({
            url: apiUrl,
            type: "GET",
            data: { date_from: startDate, date_to: endDate },
            success: function(response) {
                 displayHotels(response, startDate, endDate);
            },
            error: function(error) {
                alert("При отправке запроса произошла ошибка: " + error.responseText);
            }
        });
    });
    function displayHotels(hotels, date_from, date_to) {
    var hotelList = $(".found-hotels");

    let itemsList = [];

    if (hotels.length === 0) {
        hotelList.html("<p>Нет доступных отелей.</p>");
    } else {
        hotels.forEach(function(hotel) {
            let services = 'Нет услуг'
            if (hotel.services.length > 0) {
                services = hotel.services.join(', ')
            }
            let text =  `
            <div class="card">
                <div class="row no-gutters">
                    <div class="col-md-4">
                        <img src="/static/images/${hotel.image_id}.webp" class="card-img card-img-custom" alt="Изображение отеля">
                    </div>
                <div class="col-md-8">
                    <div class="card-body">
                        <h3 class="card-title">${hotel.name}</h3>
                        <p class="card-text">Метоположение: ${hotel.location}</p>
                        <p class="card-text">Количество комнат: ${hotel.rooms_count}</p>
                        <p class="card-text">Количество доступных комнат на выбранные даты: ${hotel.rooms_left}</p>
                        <p class="card-text">Услуги: ${services}</p>
                    </div>
                    <div class="card-footer text-right">
                        <a class="btn btn-primary" href="/hotels/${hotel.id}/rooms?date_from=${date_from}&date_to=${date_to}">Выбрать комнату</a>
                    </div>
                </div>
            </div>
`
            itemsList.push(text);
        });
    }
    hotelList.html(itemsList.join("<br>"));
}
});

