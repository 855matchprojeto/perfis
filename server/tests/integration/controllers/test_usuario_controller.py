import pytest
import uuid
from fastapi import FastAPI
from jose import jwt
from httpx import AsyncClient
from server.tests.integration import db_docker_container, cwd_to_root, create_db_upgrade, _test_client, \
    _test_app, _test_app_default_environment, get_test_async_session


class TestUsuarioController:

    """
        Testes dos métodos estáticos de UserService
    """

    # username, email, guid, roles, name
    VALID_TOKEN_GET_CURRENT_USER_ENDPOINT_PARAMETRIZE = [
        ('teste', 'teste@teste.com.br', uuid.uuid4().__str__(), [], 'Teste'),
        ('teste', 'teste@teste.com.br', uuid.uuid4().__str__(), ['2'], 'Teste'),
    ]

    @staticmethod
    @pytest.mark.asyncio
    @pytest.mark.parametrize("username, email, guid, roles, name", VALID_TOKEN_GET_CURRENT_USER_ENDPOINT_PARAMETRIZE)
    async def test_get_current_user_endpoint_valid_token(
        _test_app_default_environment: FastAPI,
        username, email, guid, roles, name
    ):
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

            response_json = response.json()
            assert response_json['username'] == username
            assert response_json['guid'] == guid

