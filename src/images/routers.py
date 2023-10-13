import os.path
import shutil

from fastapi import APIRouter, UploadFile
from starlette import status

from src.celery_conf.tasks.images import process_picture
from src.config import BASE_DIR
from src.images.exceptions import FileExistsOnServerError

image_router = APIRouter(
    prefix='/images',
)


@image_router.post(
    '/upload',
    status_code=status.HTTP_202_ACCEPTED,
)
async def upload_image(name: int, file: UploadFile):
    filepath = BASE_DIR / ('static/images/%s.webp' % str(name))
    if os.path.exists(filepath):
        raise FileExistsOnServerError
    with open(filepath, 'wb+') as destination:
        shutil.copyfileobj(file.file, destination)

    process_picture.delay(str(filepath))
