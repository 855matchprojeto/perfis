import uuid
import pytest
import time

from datetime import datetime, timedelta
from server.services.usuario_service import UsuarioService
from jose import jwt, JWTError
from mock import Mock, AsyncMock
from server.configuration import exceptions
from pydantic import EmailStr
from server.schemas.usuario_schema import CurrentUserToken


"""
    Fixtures
"""


@pytest.fixture
def user_keys_to_check_in_access_token():
    return ["guid", "name", "email", "username", "roles"]


@pytest.fixture
def expected_token_type():
    return "Bearer"


@pytest.fixture
def empty_arr():
    return []


@pytest.fixture
def single_user_arr_email_nao_verificado_db():
    """
        Retorna um usuário com um hash da senha "pass" e email nao verificado
    """
    return [
        Mock(
            id=1,
            username="user",
            email="teste@unicamp.br",
            email_verificado=False,
            hashed_password="$2a$12$AgjFKtpe9beYg10zzMNKQeEXaHbz9DF3/0xNRWr4QvJdfPcmq1Rym",
            guid=uuid.uuid4(),
            nome="Teste",
            vinculos_usuario_funcao=[
                Mock(
                    id_usuario=1,
                    id_funcao=1,
                )
            ]
        )
    ]


@pytest.fixture
def single_user_arr_email_verificado_db():
    """
        Retorna um usuário com um hash da senha "pass" e email_verificado
    """
    return [
        Mock(
            username="user",
            email="teste@unicamp.br",
            email_verificado=True,
            hashed_password="$2a$12$AgjFKtpe9beYg10zzMNKQeEXaHbz9DF3/0xNRWr4QvJdfPcmq1Rym",
            guid=uuid.uuid4(),
            nome="Teste",
            vinculos_usuario_funcao=[
                Mock(
                    id_usuario=1,
                    id_funcao=1,
                )
            ]
        )
    ]


@pytest.fixture
def verify_email_token_valid():
    """
        Retorna um token de verificação de e-mail codificado pelo
        secret_key "secret" e algoritmo "HS256"
    """

    data_to_encode = dict(
        email="teste@unicamp.br",
        username="user",
        name="Teste"
    )

    return jwt.encode(
        data_to_encode,
        "secret",
        algorithm="HS256"
    )


@pytest.fixture
def verify_email_token_expired():
    """
        Retorna um token de verificação de e-mail codificado pelo
        secret_key "secret" e algoritmo "HS256".
        O tempo de expiração desse token é expirado!
    """

    timestamp_atual = datetime.utcnow()
    timestamp_exp = timestamp_atual - timedelta(seconds=1)

    data_to_encode = dict(
        email="teste@unicamp.br",
        username="user",
        name="Teste",
        exp=timestamp_exp
    )

    return jwt.encode(
        data_to_encode,
        "secret",
        algorithm="HS256"
    )


class TestUsuarioService:

    @staticmethod
    @pytest.mark.parametrize('name, username, guid, email, roles, permissions', [
        ('Teste', 'user', uuid.uuid4().__str__(), 'teste@unicamp.br', ['1'], ['1', '2']),
        ('Teste', 'user', uuid.uuid4().__str__(), 'teste@unicamp.br', ['1'], []),
        ('Teste', 'user', uuid.uuid4().__str__(), 'teste@unicamp.br', [], ['1']),
    ])
    def test_current_user_output(name, username, guid, email: EmailStr, roles, permissions):
        curr_user = CurrentUserToken(
            name=name,
            username=username,
            guid=guid,
            email=email,
            roles=roles,
            permissions=permissions
        )

        curr_user_output = UsuarioService.current_user_output(curr_user)
        curr_user_output_dict = curr_user_output.dict()

        expected_keys = ['username', 'name', 'guid', 'email']
        for key in expected_keys:
            assert key in curr_user_output_dict

        not_expected_keys = ['roles', 'permissions']
        for key in not_expected_keys:
            assert key not in curr_user_output_dict

