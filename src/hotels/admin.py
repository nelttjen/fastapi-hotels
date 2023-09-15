from sqladmin.models import ModelView

from src.hotels.models import Hotel, Room


class HotelAdminView(ModelView, model=Hotel):
    name = 'Hotel'
    name_plural = 'Hotels'
    column_list = [Hotel.id, Hotel.name, Hotel.location, Hotel.services]
    column_details_list = [Hotel.id, Hotel.name, Hotel.location, Hotel.services, Hotel.rooms, Hotel.rooms_quantity]
    form_columns = [Hotel.name, Hotel.location, Hotel.services, Hotel.rooms_quantity, Hotel.image_id, Hotel.rooms]


class RoomAdminView(ModelView, model=Room):
    name = 'Room'
    name_plural = 'Rooms'
    column_list = [Room.id, Room.name, Room.hotel, Room.price]
    column_details_list = [Room.id, Room.name, Room.hotel, Room.price]
    form_columns = [Room.name, Room.description, Room.price, Room.services, Room.quantity, Room.image_id, Room.hotel]
