import os

from server import _init_app
import uvicorn
from server.dependencies.get_environment_cached import get_environment_cached


if __name__ == '__main__':
    app = _init_app()
    print(os.getenv('PYTHONPATH'))
    environment = get_environment_cached()
    uvicorn.run(app, host=environment.HOST, port=environment.PORT)

