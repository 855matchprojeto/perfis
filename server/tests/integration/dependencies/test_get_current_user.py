import pytest
import uuid
from fastapi import FastAPI
from server.tests.integration import db_docker_container, cwd_to_root, create_db_upgrade, _test_client, \
    _test_app, _test_app_default_environment, get_test_async_session
from fastapi.testclient import TestClient
from jose import jwt
from datetime import datetime, timedelta
from fastapi.security import SecurityScopes
from server.dependencies.get_security_scopes import get_security_scopes
from mock import Mock
from server.tests.integration import build_test_async_session_maker
from server.models.permissao_model import Permissao
from server.models.vinculo_permissao_funcao_model import VinculoPermissaoFuncao
from httpx import AsyncClient


def all_perms():
    perms = ['P1', 'P2', 'P3', 'P4']
    return Mock(
        scopes=perms,
        scope_str=",".join(perms)
    )


@pytest.fixture
async def write_mock_permissions_db():
    """
        Criando permissões e funções MOCK para o banco de dados
        (F1 -> P1, P2, P3)
        (F2 -> P4)
        (F3 -> )
    """

    session_maker = build_test_async_session_maker()

    async with session_maker() as session:

        # Criando função F1 -> Ligada a várias permissoes (P1, P2, P3)

        perm1 = Permissao(nome='P1')
        perm2 = Permissao(nome='P2')
        perm3 = Permissao(nome='P3')

        session.add_all([perm1, perm2, perm3])
        await session.flush()

        for perm in [perm1, perm2, perm3]:
            session.add(
                VinculoPermissaoFuncao(
                    id_funcao=1,
                    id_permissao=perm.id
                )
            )

        await session.flush()

        # Criando função F2 -> Ligada apenas a uma permissao P4

        perm4 = Permissao(nome='P4')
        session.add_all([perm4])
        await session.flush()

        session.add(
            VinculoPermissaoFuncao(
                id_funcao=2,
                id_permissao=perm4.id
            )
        )

        await session.flush()
        await session.commit()
        await session.close()


@pytest.fixture
def current_user_token_valid():

    data_to_encode = {
        "username": "user",
        "email": "teste@teste.com",
        "guid": uuid.uuid4().__str__(),
        "roles": [1],
        "name": "Teste"
    }

    return jwt.encode(
        data_to_encode,
        "secret",
        algorithm="HS256"
    )


@pytest.fixture
def current_user_token_wrong_secret():

    data_to_encode = {
        "username": "user",
        "email": "teste@teste.com",
        "guid": uuid.uuid4().__str__(),
        "roles": [1],
        "name": "Teste"
    }

    return jwt.encode(
        data_to_encode,
        "wrong",
        algorithm="HS256"
    )


@pytest.fixture
def current_user_token_expired():

    timestamp_atual = datetime.utcnow()
    timestamp_exp = timestamp_atual - timedelta(seconds=1)

    data_to_encode = {
        "username": "user",
        "email": "teste@teste.com",
        "guid": uuid.uuid4().__str__(),
        "roles": [1],
        "name": "Teste",
        "exp": timestamp_exp
    }

    return jwt.encode(
        data_to_encode,
        "wrong",
        algorithm="HS256"
    )


@pytest.fixture
def current_user_wrong_schema():

    data_to_encode = {
        "username": "user",
        "email": "teste@teste.com",
        "guid": uuid.uuid4().__str__(),
        "roles": [1],
        "nome": "Teste",  # "nome" ao inves de "name"
    }

    return jwt.encode(
        data_to_encode,
        "wrong",
        algorithm="HS256"
    )


class TestUsuarioService:

    """
        Testes dos métodos estáticos de UserService
    """

    # username, email, guid, roles, name, security_scopes_overrider
    ENOUGH_PERMISSION_DATA = [
        ('teste', 'teste@teste.com.br', uuid.uuid4().__str__(), ['1', '2', '3'], 'Teste', all_perms),
        ('teste', 'teste@teste.com.br', uuid.uuid4().__str__(), ['1', '2'], 'Teste', all_perms),
    ]

    # username, email, guid, roles, name, security_scopes_overrider
    NOT_ENOUGH_PERMISSION_DATA = [
        ('teste', 'teste@teste.com.br', uuid.uuid4().__str__(), ['2', '3'], 'Teste', all_perms),
        ('teste', 'teste@teste.com.br', uuid.uuid4().__str__(), ['1'], 'Teste', all_perms),
    ]

    @staticmethod
    @pytest.mark.asyncio
    async def test_get_current_user_no_headers(_test_app_default_environment: FastAPI, _test_client: TestClient):

        async with AsyncClient(
                app=_test_app_default_environment,
                base_url='http://test'
        ) as test_async_client:

            test_async_client: AsyncClient

            response = await test_async_client.get(
                'users/me',
            )
            assert response.status_code == 401

    @staticmethod
    @pytest.mark.asyncio
    async def test_get_current_user_wrong_secret(
        _test_app_default_environment: FastAPI, _test_client: TestClient,
        current_user_token_wrong_secret
    ):

        async with AsyncClient(
                app=_test_app_default_environment,
                base_url='http://test'
        ) as test_async_client:

            test_async_client: AsyncClient

            response = await test_async_client.get(
                'users/me',
                headers=dict(
                    Authorization=f"Bearer {current_user_token_wrong_secret}"
                ),
            )
        assert response.status_code == 401

    @staticmethod
    @pytest.mark.asyncio
    async def test_get_current_user_expired_token(
        _test_app_default_environment: FastAPI, _test_client: TestClient,
        current_user_token_expired
    ):

        async with AsyncClient(
                app=_test_app_default_environment,
                base_url='http://test'
        ) as test_async_client:

            test_async_client: AsyncClient

            response = await test_async_client.get(
                'users/me',
                headers=dict(
                    Authorization=f"Bearer {current_user_token_expired}"
                ),
            )
            assert response.status_code == 401

    @staticmethod
    @pytest.mark.asyncio
    async def test_get_current_user_wrong_schema_validation(
        _test_app_default_environment: FastAPI, _test_client: TestClient,
        current_user_wrong_schema
    ):
        async with AsyncClient(
                app=_test_app_default_environment,
                base_url='http://test'
        ) as test_async_client:

            test_async_client: AsyncClient

            response = await test_async_client.get(
                'users/me',
                headers=dict(
                    Authorization=f"Bearer {current_user_wrong_schema}"
                ),
            )
            assert response.status_code == 401

    @staticmethod
    @pytest.mark.asyncio
    @pytest.mark.parametrize("username, email, guid, roles, name, security_scopes_overrider",
                             ENOUGH_PERMISSION_DATA)
    async def test_current_user_enough_permissions(
        _test_app_default_environment: FastAPI, _test_client: TestClient,
        username, email, guid, roles, security_scopes_overrider,
        name, write_mock_permissions_db
    ):
        _test_app_default_environment.dependency_overrides[get_security_scopes] = security_scopes_overrider

        data_to_encode = dict(
            username=username,
            email=email,
            guid=guid,
            roles=roles,
            name=name
        )

        usr_token = jwt.encode(
            data_to_encode,
            'secret',
            algorithm="HS256"
        )

        async with AsyncClient(
                app=_test_app_default_environment,
                base_url='http://test'
        ) as test_async_client:

            test_async_client: AsyncClient

            response = await test_async_client.get(
                'users/me',
                headers=dict(
                    Authorization=f"Bearer {usr_token}"
                ),
            )

            assert response.status_code == 200

    @staticmethod
    @pytest.mark.asyncio
    @pytest.mark.parametrize("username, email, guid, roles, name, security_scopes_overrider",
                             NOT_ENOUGH_PERMISSION_DATA)
    async def test_current_user_not_enough_permissions(
            _test_app_default_environment: FastAPI, _test_client: TestClient,
            username, email, guid, roles, security_scopes_overrider,
            name, write_mock_permissions_db
    ):
        _test_app_default_environment.dependency_overrides[get_security_scopes] = security_scopes_overrider

        data_to_encode = dict(
            username=username,
            email=email,
            guid=guid,
            roles=roles,
            name=name
        )

        usr_token = jwt.encode(
            data_to_encode,
            'secret',
            algorithm="HS256"
        )

        async with AsyncClient(
                app=_test_app_default_environment,
                base_url='http://test'
        ) as test_async_client:

            test_async_client: AsyncClient

            response = await test_async_client.get(
                'users/me',
                headers=dict(
                    Authorization=f"Bearer {usr_token}"
                ),
            )

            assert response.status_code == 401

