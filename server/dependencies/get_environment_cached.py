from server.configuration.environment import Environment
from functools import lru_cache
import pathlib


@lru_cache
def get_environment_cached():
    return Environment(
        _env_file=f"{str(pathlib.Path(__file__).parents[2])}/.env/PROJETOS.env",
        _env_file_encoding="utf-8"
    )

