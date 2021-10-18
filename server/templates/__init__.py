from fastapi.templating import Jinja2Templates
from pathlib import Path

jinja2_templates = Jinja2Templates(directory=str(Path(__file__).parent.parent / 'templates'))


