from fastapi import Depends
from server.dependencies.oauth2 import oauth2_scheme
from server.dependencies.session import get_session
from server.configuration.db import AsyncSession
from server.schemas.usuario_schema import CurrentUserToken
from jose import JWTError, jwt
from server.configuration import exceptions
from pydantic import ValidationError
from server.schemas.token_shema import DecodedAccessToken
from server.repository.permissao_repository import PermissaoRepository
from starlette_context import context
from server.configuration.custom_logging import get_main_logger
from server.dependencies.get_environment_cached import get_environment_cached
from server.configuration.environment import Environment
from server.dependencies.get_security_scopes import get_security_scopes
from fastapi.security import SecurityScopes


MAIN_LOGGER = get_main_logger()


async def get_current_user(
    required_security_permission_scopes: SecurityScopes = Depends(get_security_scopes),
    session: AsyncSession = Depends(get_session),
    token: str = Depends(oauth2_scheme),
    environment: Environment = Depends(get_environment_cached)
) -> CurrentUserToken:

    try:

        """
            Verifique se o token foi expirado ou é inválido
    
            Verifica as permissões requeridas pelo endpoint atual
            em required_security_permission_scopes e compara com as
            permissões vinculadas às funções do usuário
    
            Se as condições forem satisfeitas, retorna o usuário
            atual, que fez a requisição
        """

        MAIN_LOGGER.info("Início da rotina de decodificação de token do usuário")

        try:
            decoded_token_dict = jwt.decode(
                token,
                environment.ACCESS_TOKEN_SECRET_KEY,
                algorithms=[environment.ACCESS_TOKEN_ALGORITHM]
            )
            decoded_token = DecodedAccessToken(**decoded_token_dict)
        except (JWTError, ValidationError) as ex:
            raise exceptions.InvalidExpiredTokenException()

        permission_repo = PermissaoRepository(session)
        roles = [int(role) for role in decoded_token.roles]

        user_dict = {
            'username': decoded_token.username,
            'email': decoded_token.email,
            'guid': decoded_token.guid,
            'name': decoded_token.name,
            'roles': roles
        }

        if len(required_security_permission_scopes.scopes) > 0:
            user_permissions = await permission_repo.find_permissions_by_roles_list(roles)
            user_permissions_names = [permission.nome for permission in user_permissions]

            for required_permission_scope in required_security_permission_scopes.scopes:
                if required_permission_scope not in user_permissions_names:
                    raise exceptions.NotEnoughPermissionsException(
                        detail=f'O usuário {decoded_token.username}'
                               f' não tem as permissões necessárias para acessar esse recurso'
                    )

        current_user = CurrentUserToken(**user_dict)

        # Determina o contexto para que o usuário possa ser recuperado globalmente
        context.data['current_user'] = current_user

        MAIN_LOGGER.info("Fim da rotina de decodificação de token de usuário. O usuário foi autenticado e autorizado")

        return current_user

    except Exception as ex:
        await session.rollback()
        raise ex
    finally:
        await session.close()

