import os.path
import shutil
from fastapi import APIRouter, UploadFile
from src.config import BASE_DIR
from src.images.exceptions import FileExistsOnServerError

image_router = APIRouter(
    prefix='/images',
    tags=['images'],
)


@image_router.post('/upload')
async def upload_image(name: int, file: UploadFile):
    filepath = BASE_DIR / ('static/images/%s.webp' % str(name))
    if os.path.exists(filepath):
        raise FileExistsOnServerError
    with open(filepath, 'wb+') as destination:
        shutil.copyfileobj(file.file, destination)
