import os
from pathlib import Path

from PIL import Image

from src.celery.celery import celery_app


@celery_app.task
def process_picture(
        path: str,
) -> bool:
    path = Path(path)
    image = Image.open(path)
    resized_1920_1080 = image.resize((1920, 1080))
    resized_1024_562 = image.resize((1024, 562))
    resized_200_100 = image.resize((1024, 576))

    path_resized = Path('static/images/resized/')
    if not os.path.exists(path_resized):
        os.mkdir(path_resized)

    for image, resolution in [
        (resized_1920_1080, '1920_1080'), (resized_1024_562, '1024_562'), (resized_200_100, '200_100'),
    ]:
        if not os.path.exists(path_resized / f'{resolution}'):
            os.mkdir(path_resized / f'{resolution}')
        image.save(path_resized / f'{resolution}' / f'resized_{resolution}_{path.name}')

    return True
