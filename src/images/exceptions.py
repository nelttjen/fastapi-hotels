from src.base.exceptions import DataConflict


class FileExistsOnServerError(DataConflict):
    detail = 'File with this id already exists'
