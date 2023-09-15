async function updateClick(){
    $(".add-favourite").click(async function (e) {
        await validateToken();
        while (!authHeaders) {
            await new Promise(resolve => {
                setTimeout(() => {resolve()}, 1000);
            })
        }
        await new Promise(resolve => {
            setTimeout(() => {resolve()}, 200);
        })
        e.preventDefault();
        let val = $(e.target).attr("hotel-id")
        $.ajax({
            'method': 'POST',
            'url': `/api/v1/hotels/my/favourites/${val}`,
            headers: authHeaders,
            success: function(data) {
                $(e.target).disable();
            }
        })
    });
}

$(document).ready(async function() {
    $(function(){
        $('#startDate').prop('min', function(){
            return tomorrow.toJSON().split('T')[0];
        });
        $('#endDate').prop('min', function(){
            return day2fw.toJSON().split('T')[0];
        });
    });
    $("#search-button").click(async function(event) {
        event.preventDefault();

        var title = $("#title").val();
        var startDate = $("#startDate").val();
        var endDate = $("#endDate").val();

        var apiUrl = "/api/v1/hotels/search/" + encodeURIComponent(title);

        if (!title || !startDate || !endDate) {
            alert("You must fill the search field, date from and date to fields!");
            return;
        }

        $.ajax({
            url: apiUrl,
            type: "GET",
            data: { date_from: startDate, date_to: endDate },
            success: async function(response) {
                 await displayHotels(response, startDate, endDate);
            },
            error: function(error) {
                alert(error.responseJSON.detail);
            }
        });
    });
    async function displayHotels(hotels, date_from, date_to) {
        var hotelList = $(".found-hotels");

        let itemsList = [];

        if (hotels.length === 0) {
            hotelList.html(
                "<p>There's no available hotels with current filters.</p>" +
                "<p>Please try again with different filters.</p>"
            );
        } else {
            hotels.forEach(function(hotel) {
                let services = 'No information about services'
                if (hotel.services.length > 0) {
                    services = hotel.services.join(', ')
                }
                let text =  `
                <div class="card">
                    <div class="row no-gutters">
                        <div class="col-md-4">
                            <img src="/static/images/${hotel.image_id}.webp" class="card-img card-img-custom" alt="Hotel image">
                        </div>
                    <div class="col-md-8">
                        <div class="card-body">
                            <h3 class="card-title">${hotel.name}</h3>
                            <p class="card-text">Location: ${hotel.location}</p>
                            <p class="card-text">Rooms count: ${hotel.rooms_count}</p>
                            <p class="card-text">Rooms left for the choosen dates: ${hotel.rooms_left}</p>
                            <p class="card-text">Services: ${services}</p>
                        </div>
                        <div class="card-footer text-right">
                            <a class="btn btn-primary" href="/hotels/${hotel.id}/rooms?date_from=${date_from}&date_to=${date_to}">Choose a room</a>
                            <a class="btn btn-success add-favourite" hotel-id="${hotel.id}">Add to favourite</a>
                        </div>
                    </div>
                </div>
        `
                itemsList.push(text);
            });
        }
        hotelList.html(itemsList.join("<br>"));
        await updateClick();
    }
});
