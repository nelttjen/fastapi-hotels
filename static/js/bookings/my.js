function fillTable(bookings) {
    let tbody = $(".my-bookings-list");

    bookings.forEach(function (booking) {
        var row = $("<tr class='order-row'>");
        row.html(`
            <td><a href="/hotels/${booking.room.hotel_id}/rooms${defaultQueryDate}" class=".order-field" field-data="hotel">${booking.room.hotel.name}</a></td>
            <td class=".order-field" field-data="room">${booking.room.name}</td>
            <td class=".order-field" field-data="from">${booking.date_from}</td>
            <td class=".order-field" field-data="to">${booking.date_to}</td>
            <td class=".order-field" field-data="price">${booking.total_cost}</td>
            <td class=".order-field" field-data="days">${booking.total_days}</td>
            <td>
            <a href="/bookings/my/${booking.id}" class="btn btn-primary">Info</a>
            </td>

        `);
        tbody.append(row);
    });
}

async function fetchBookingsData(queryParams) {
    $.ajax({
        method: 'GET',
        url: '/api/v1/bookings/my' + queryParams,
        headers: authHeaders,
        success: function(data) {
            fillTable(data);
        },
        error: function(data) {
            if (data.status === 401) {
                window.location.href = '/auth/login';
            } else if (data.status === 422) {
                displayPydanticErrors(data.responseJSON.detail);
            } else alert(data.responseJSON.detail);
        }
    })
}

$(document).ready(async function() {
    await validateToken();
    while (!authHeaders) {
        await new Promise(resolve => {
            setTimeout(() => {resolve()}, 1000);
        })
    }
    await new Promise(resolve => {
        setTimeout(() => {resolve()}, 100);
    })
    // alert(`logged in as ${authHeaders['Authorization']}`);
    await fetchBookingsData("");

    const headers = document.querySelectorAll("th[data-column]");
    let currentOrder = null;

    headers.forEach(header => {
        header.addEventListener("click", () => {
            const column = header.getAttribute("data-column");
            currentOrder = currentOrder === column ? `-${column}` : column;

            headers.forEach(h => h.classList.remove("sort-asc", "sort-desc"));

            header.classList.add(currentOrder.startsWith("-") ? "sort-desc" : "sort-asc");
            filterRows(currentOrder);
        });
    });

    function filterRows(filterBy) {
        let rows = $('.order-row');
        let filter = "str";

        if (filterBy === "days" || filterBy === "price" || filterBy === "-price" || filterBy === "-days") {
            filter = "int";
        }

        rows.sort(function(a, b) {
            let aValue = $(a).find(`[field-data="${filterBy.replace('-', '')}"]`).text();
            let bValue = $(b).find(`[field-data="${filterBy.replace('-', '')}"]`).text();

            if (filter === "int") {
                aValue = parseInt(aValue);
                bValue = parseInt(bValue);
                if (filterBy.startsWith("-")) {
                    return bValue > aValue;
                } else {
                    return aValue > bValue;
                }
            } else {
            if (filterBy.startsWith("-")) {
                return bValue.localeCompare(aValue);
            } else {
                return aValue.localeCompare(bValue);
            }
            }


        });

        $('.my-bookings-list').empty().append(rows);
    }
});
