from src.base.exceptions import BadRequest, DataConflict, Forbidden


class NoRoomsAvailable(DataConflict):
    detail = 'No rooms available for chosen dates'
    