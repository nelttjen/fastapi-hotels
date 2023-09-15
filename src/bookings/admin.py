from sqladmin.models import ModelView

from src.bookings.models import Booking


class BookingAdminView(ModelView, model=Booking):
    name = 'Booking'
    name_plural = 'Bookings'
    column_list = [Booking.id, Booking.user, Booking.room,
                   Booking.date_from, Booking.date_from, Booking.total_days, Booking.total_cost]
    column_details_list = [
        Booking.id, Booking.date_from, Booking.date_to, Booking.price, Booking.total_days, Booking.total_cost,
        Booking.user, Booking.room,
    ]
    form_columns = [
        Booking.date_from, Booking.date_to, Booking.price, Booking.room, Booking.user,
    ]
    column_searchable_list = [Booking.user_id, Booking.room_id]
