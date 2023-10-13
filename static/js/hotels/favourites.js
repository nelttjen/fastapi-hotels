function updateClick(){
    $(".delete-favourite").click((e) => {
        e.preventDefault();
        let val = $(e.target).attr("hotel_id")
        $.ajax({
            'method': 'DELETE',
            'url': `/api/v1/hotels/my/favourites/${val}`,
            headers: authHeaders,
            success: function(data) {
                $(`.hotel-${val}`).remove();
            }
        })
    });
}

function fillTable(hotels) {
    let tbody = $(".my-favourites-list");

    hotels.forEach(function (hotel) {
        var row = $(`<tr class='order-row hotel-${hotel.id}'>)`);
        row.html(`
            <td><a href="/hotels/${hotel.id}/rooms${defaultQueryDate}" class=".order-field" field-data="hotel">${hotel.name}</a></td>
            <td class=".order-field" field-data="location">${hotel.location}</td>
            <td class=".order-field" field-data="rooms">${hotel.rooms_count}</td>
            <td>
            <btn class="btn btn-danger delete-favourite" hotel_id="${hotel.id}">D</btn>
            </td>
        `);
        tbody.append(row);
    });
    updateClick();
}

async function fetchFavouritesData() {
    $.ajax({
        method: 'GET',
        url: '/api/v1/hotels/my/favourites',
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
        setTimeout(() => {resolve()}, 200);
    })

    await fetchFavouritesData();
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

        if (filterBy === "rooms" || filterBy === "-rooms") {
            filter = "int";
        }

        rows.sort(function (a, b) {
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

        $('.my-favourites-list').empty().append(rows);
    }
});
