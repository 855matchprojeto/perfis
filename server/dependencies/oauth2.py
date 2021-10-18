"""
    Os tokens definirão scopes baseados nas FUNÇÕES dos usuários

    Os endpoints definirão scopes baseados em PERMISSÕES
    Cada FUNÇÃO pode ter várias PERMISSÕES vinculadas
"""

from fastapi.security import OAuth2PasswordBearer
from server.configuration.environment import AuthEnvironment
import pathlib

environment = AuthEnvironment(
    _env_file=f"{str(pathlib.Path(__file__).parents[2])}/.env/PROJETOS.env",
    _env_file_encoding="utf-8"
)

oauth2_scheme = OAuth2PasswordBearer(
    tokenUrl=f'{environment.AUTHENTICATOR_DNS}/users/token'
)

