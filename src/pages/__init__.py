from fastapi.templating import Jinja2Templates

from src.config import BASE_DIR

templates = Jinja2Templates(directory=BASE_DIR / 'templates')
