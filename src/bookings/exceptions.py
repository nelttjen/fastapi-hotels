from src.base.exceptions import DataConflict


class NoRoomsAvailable(DataConflict):
    detail = 'No rooms available for chosen dates'
