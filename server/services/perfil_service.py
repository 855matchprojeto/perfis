from server.configuration import exceptions
from jose import jwt
from typing import List, Optional
from fastapi import Request
from server.configuration.environment import Environment
from server.schemas.usuario_schema import CurrentUserToken
from server.repository.perfil_repository import PerfilRepository
from server.repository.interesse_repository import InteresseRepository
from server.repository.curso_repository import CursoRepository
from server.schemas.cursor_schema import Cursor
from server.models.perfil_model import Perfil
from server import utils
from server.schemas.perfil_schema import PerfilInput, PerfilPostInput, PerfilPatchInput, NotOwnerPerfilPostInput
from server.models.curso_model import Curso
from server.models.interesse_model import Interesse
from server.schemas.perfil_email_schema import PerfilEmailPostInput, PerfilEmailPatchInput
from server.schemas.perfil_phone_schema import PerfilPhonePostInput, PerfilPhonePatchInput
from server.repository.tipo_contato_repository import TipoContatoRepository
from server.models.tipo_contato_model import TipoContato
from server.services.arquivo_service import ArquivoService
from server.models.arquivo_model import Arquivo
from server.schemas.perfil_schema import UsuarioPostInput
from server.repository.usuario_repository import UsuarioRepository


class PerfilService:

    @staticmethod
    def get_filter_factory():
        return {
            "interests_in": InteresseRepository.get_interests_in_filter,
            "courses_in": CursoRepository.get_courses_in_filter,
            "display_name_ilike": PerfilRepository.get_name_ilike_filter
        }

    @staticmethod
    def get_filters_by_params(params_dict: dict):
        filters = []
        filter_factory = PerfilService.get_filter_factory()
        for key in params_dict:
            param = params_dict[key]
            if param:
                filters.extend(filter_factory[key](param))
        return filters

    @staticmethod
    def get_previous_url(request: Request):
        return str(request.url)

    @staticmethod
    def get_next_url(request: Request, path: str, next_encoded_cursor: str):
        if not next_encoded_cursor:
            return None

        query_params_dict = dict(request.query_params)
        query_string_builder = '?'

        for query_param_key in [key for key in query_params_dict.keys() if key != 'cursor']:
            query_param_value = query_params_dict[query_param_key]
            query_string_builder += f'{query_param_key}={query_param_value}&'

        query_string_builder += f'cursor={next_encoded_cursor}'

        return f"{request.base_url}{path}{query_string_builder}"

    @staticmethod
    def handle_profile_body(perfil: Perfil):
        perfil.interesses = [
            x.interesse for x in perfil.vinculos_perfil_interesse
        ]
        perfil.cursos = [
            x.curso for x in perfil.vinculos_perfil_curso
        ]
        return perfil

    @staticmethod
    def handle_profile_body_list(perfil_list: List[Perfil]):
        for perfil in perfil_list:
            PerfilService.handle_profile_body(perfil)
        return perfil_list

    @staticmethod
    def handle_profile_pagination(
        paginated_profile_dict: dict, previous_encoded_cursor: str, request: Request
    ):
        next_encoded_cursor = paginated_profile_dict['next_cursor']

        paginated_profile_dict['items'] = PerfilService.handle_profile_body_list(paginated_profile_dict['items'])
        paginated_profile_dict['previous_cursor'] = previous_encoded_cursor
        paginated_profile_dict['previous_url'] = PerfilService.get_previous_url(request)
        paginated_profile_dict['next_url'] = PerfilService.get_next_url(request, request.url.path, next_encoded_cursor)

        return paginated_profile_dict

    @staticmethod
    def validate_current_user_to_input(current_user: CurrentUserToken, perfil_input):
        return (
            perfil_input.guid_usuario == current_user.guid
        )

    def __init__(
        self,
        perfil_repo: Optional[PerfilRepository] = None,
        curso_repo: Optional[CursoRepository] = None,
        interesse_repo: Optional[InteresseRepository] = None,
        tipo_contato_repo: Optional[TipoContatoRepository] = None,
        usuario_repo: Optional[UsuarioRepository] = None,
        environment: Optional[Environment] = None,
        arquivo_service: Optional[ArquivoService] = None
    ):
        self.perfil_repo = perfil_repo
        self.curso_repo = curso_repo
        self.interesse_repo = interesse_repo
        self.tipo_contato_repo = tipo_contato_repo
        self.usuario_repo = usuario_repo

        self.environment = environment
        self.arquivo_service = arquivo_service

    def decode_cursor_info(self, encoded_cursor: str):
        decoded_cursor_dict = jwt.decode(
            encoded_cursor,
            self.environment.CURSOR_TOKEN_SECRET_KEY,
            algorithms=[self.environment.CURSOR_TOKEN_ALGORITHM]
        )
        return Cursor(**decoded_cursor_dict)

    async def get_profile_by_guid(self, guid_profile: str):
        perfil = await self.perfil_repo.find_profile_by_guid(guid_profile)
        if not perfil:
            raise exceptions.ProfileNotFoundException(
                detail=f"O perfil de GUID={guid_profile} n??o foi encontrado."
            )
        return self.handle_profile_body(perfil)

    async def get_profile_by_guid_usuario(self, guid_usuario: str):
        perfil = await self.perfil_repo.find_profile_by_guid_usuario(guid_usuario)
        if not perfil:
            raise exceptions.ProfileNotFoundException(
                detail=f"O perfil do usu??rio de GUID={guid_usuario} n??o foi encontrado."
            )
        return self.handle_profile_body(perfil)

    async def get_all_profiles_paginated(
        self, filter_params_dict: dict,
        request: Request, limit: int, cursor: str
    ):
        filters = PerfilService.get_filters_by_params(filter_params_dict)
        decoded_cursor = self.decode_cursor_info(cursor) if cursor else None
        previous_encoded_cursor = decoded_cursor.previous_encoded_cursor if decoded_cursor else None

        paginated_profile_dict = await self.perfil_repo.\
            find_profiles_by_filters_paginated(limit, cursor, decoded_cursor, filters)

        paginated_profile_dict = PerfilService.handle_profile_pagination(
            paginated_profile_dict, previous_encoded_cursor, request
        )

        return paginated_profile_dict

    async def create_profile_by_guid_usuario(self, current_user: CurrentUserToken, profile_input: PerfilPostInput):
        # Verificando se ja existe um perfil para o usu??rio
        perfil_db = await self.perfil_repo.find_profile_by_guid_usuario(
            current_user.guid,
            load_all_entities=False
        )
        if perfil_db:
            raise exceptions.ProfileConflictException(
                detail=f"J?? existe um perfil cadastrado para o usu??rio {current_user.guid}"
            )
        # L??gica padr??o do endpoint de inser????o de perfil
        profile_dict = profile_input.convert_to_dict()
        profile_dict['guid_usuario'] = current_user.guid
        # Preenchendo nome exibi????o e normalizacao se existir
        nome_exibicao = profile_dict.get('nome_exibicao')
        profile_dict['nome_exibicao_normalized'] = (
            utils.normalize_string(nome_exibicao)
            if nome_exibicao
            else None
        )
        return await self.perfil_repo.insere_perfil(profile_dict)

    async def handle_input_imagem_perfil(
        self, current_user: CurrentUserToken, profile_input: PerfilInput
    ) -> Optional[Arquivo]:
        """
            Cria o arquivo da imagem de perfil do usuario e vincula
            o id do arquivo criado no input
        """

        imagem_perfil_input = profile_input.imagem_perfil
        if imagem_perfil_input:
            imagem_perfil = await self.arquivo_service.upload_arquivo(imagem_perfil_input, current_user)

            profile_input.id_imagem_perfil = imagem_perfil.id
            profile_input.imagem_perfil = None

            return imagem_perfil

        return None

    async def patch_profile_by_guid_usuario(self, current_user: CurrentUserToken, profile_input: PerfilPatchInput):
        await self.handle_input_imagem_perfil(current_user, profile_input)

        profile_dict = profile_input.convert_to_dict(exclude_unset=True)

        # Preenchendo nome exibi????o e normalizacao se existir
        nome_exibicao = profile_dict.get('nome_exibicao')
        profile_dict['nome_exibicao_normalized'] = (
            utils.normalize_string(nome_exibicao)
            if nome_exibicao
            else None
        )

        await self.perfil_repo.atualiza_perfil_by_guid_usuario(current_user.guid, profile_dict)
        return await self.perfil_repo.find_profile_by_guid_usuario(current_user.guid)

    async def delete_profile_by_guid_usuario(self, guid_usuario: str):
        # Verificando se existe um usuario no banco
        perfil = await self.perfil_repo.find_profile_by_guid_usuario(
            guid_usuario, load_all_entities=False
        )
        if not perfil:
            raise exceptions.ProfileNotFoundException(
                detail=f"O perfil do usu??rio de GUID={guid_usuario} n??o foi encontrado."
            )
        # Capturando o ID do perfil
        return await self.perfil_repo.delete_perfil(perfil.id)

    async def link_course_to_profile(self, guid_usuario, id_curso: int):
        cursos = await self.curso_repo.find_all_courses_by_filters(
            [Curso.id == id_curso]
        )
        if not cursos:
            raise exceptions.CourseNotFoundException(
                detail=f"N??o foi encontrado um curso com ID = {id_curso}"
            )
        curso = cursos[0]

        perfil = await self.perfil_repo.find_profile_by_guid_usuario(
            guid_usuario,
            load_all_entities=False
        )
        if not perfil:
            raise exceptions.ProfileNotFoundException(
                detail=f"N??o foi encontrado um perfil para o usu??rio {guid_usuario}"
            )

        vinculo_db = await self.perfil_repo.find_vinculo_perfil_curso(
            curso.id,
            perfil.id
        )
        if vinculo_db:
            raise exceptions.CourseLinkConflictException(
                detail=f"J?? existe um v??nculo do perfil do usu??rio {guid_usuario}"
                       f" com o curso de ID = {id_curso}"
            )

        await self.perfil_repo.insert_vinculo_perfil_curso(
            curso.id,
            perfil.id
        )

    async def delete_profile_course_link(self, guid_usuario, id_curso: int):
        cursos = await self.curso_repo.find_all_courses_by_filters(
            [Curso.id == id_curso]
        )
        if not cursos:
            raise exceptions.CourseNotFoundException(
                detail=f"N??o foi encontrado um curso com ID = {id_curso}"
            )
        curso = cursos[0]

        perfil = await self.perfil_repo.find_profile_by_guid_usuario(
            guid_usuario,
            load_all_entities=False
        )
        if not perfil:
            raise exceptions.ProfileNotFoundException(
                detail=f"N??o foi encontrado um perfil para o usu??rio {guid_usuario}"
            )

        vinculo_db = await self.perfil_repo.find_vinculo_perfil_curso(
            curso.id,
            perfil.id
        )
        if not vinculo_db:
            raise exceptions.CourseLinkNotFoundException(
                detail=f"N??o existe um v??nculo do perfil do usu??rio {guid_usuario}"
                       f" com o curso de ID = {id_curso}"
            )

        await self.perfil_repo.delete_vinculo_perfil_curso(
            curso.id,
            perfil.id
        )

    async def link_interest_to_profile(self, guid_usuario, id_interesse: int):
        interesses = await self.interesse_repo.find_all_interests_by_filters(
            [Interesse.id == id_interesse]
        )
        if not interesses:
            raise exceptions.InterestNotFoundException(
                detail=f"N??o foi encontrado um interesse com ID = {id_interesse}"
            )
        interesse = interesses[0]

        perfil = await self.perfil_repo.find_profile_by_guid_usuario(
            guid_usuario,
            load_all_entities=False
        )
        if not perfil:
            raise exceptions.ProfileNotFoundException(
                detail=f"N??o foi encontrado um perfil para o usu??rio {guid_usuario}"
            )

        vinculo_db = await self.perfil_repo.find_vinculo_perfil_interesse(
            interesse.id,
            perfil.id
        )
        if vinculo_db:
            raise exceptions.InterestLinkConflictException(
                detail=f"J?? existe um v??nculo do perfil do usu??rio {guid_usuario}"
                       f" com o interesse de ID = {id_interesse}"
            )

        await self.perfil_repo.insert_vinculo_perfil_interesse(
            interesse.id,
            perfil.id
        )

    async def delete_profile_interest_link(self, guid_usuario, id_interesse: int):
        interesses = await self.interesse_repo.find_all_interests_by_filters(
            [Interesse.id == id_interesse]
        )
        if not interesses:
            raise exceptions.InterestNotFoundException(
                detail=f"N??o foi encontrado um interesse com ID = {id_interesse}"
            )
        interesse = interesses[0]

        perfil = await self.perfil_repo.find_profile_by_guid_usuario(
            guid_usuario,
            load_all_entities=False
        )
        if not perfil:
            raise exceptions.ProfileNotFoundException(
                detail=f"N??o foi encontrado um perfil para o usu??rio {guid_usuario}"
            )

        vinculo_db = await self.perfil_repo.find_vinculo_perfil_interesse(
            interesse.id,
            perfil.id
        )
        if not vinculo_db:
            raise exceptions.InterestLinkNotFoundException(
                detail=f"N??o existe um v??nculo do perfil do usu??rio {guid_usuario}"
                       f" com o interesse de ID = {id_interesse}"
            )

        await self.perfil_repo.delete_vinculo_perfil_interesse(
            interesse.id,
            perfil.id
        )

    async def insert_email_profile_by_guid_usuario(
        self, guid_usuario: str, perfil_email_input: PerfilEmailPostInput
    ):

        # Procurando o perfil a partir do guid do usu??rio
        perfil = await self.perfil_repo.find_profile_by_guid_usuario(
            guid_usuario,
            load_all_entities=False
        )
        if not perfil:
            raise exceptions.ProfileNotFoundException(
                detail=f"N??o foi encontrado um perfil para o usu??rio {guid_usuario}"
            )

        # Inserindo no banco de dados
        perfil_email_dict = perfil_email_input.convert_to_dict()
        perfil_email_dict['id_perfil'] = perfil.id
        return await self.perfil_repo.insert_email_profile(perfil_email_dict)

    async def patch_email_profile_by_guid(
        self, guid_perfil_email: str, perfil_email_patch_input: PerfilEmailPatchInput
    ):

        # Procurando a entidade de PerfilEmail a partir do guid do perfil_email
        perfil_email = await self.perfil_repo.find_perfil_email_by_guid(
            guid_perfil_email
        )
        if not perfil_email:
            raise exceptions.ProfileEmailNotFoundException(
                detail=f"N??o foi encontrado a entidade de PerfilEmail de GUID = {guid_perfil_email}"
            )

        # Inserindo no banco de dados
        perfil_email_patch_dict = perfil_email_patch_input.convert_to_dict()
        return await self.perfil_repo.atualiza_email_profile(
            guid_perfil_email,
            perfil_email_patch_dict
        )

    async def delete_email_profile_by_guid(
        self, guid_perfil_email: str
    ):

        # Procurando a entidade de PerfilEmail a partir do guid do perfil_email
        perfil_email = await self.perfil_repo.find_perfil_email_by_guid(
            guid_perfil_email
        )
        if not perfil_email:
            raise exceptions.ProfileEmailNotFoundException(
                detail=f"N??o foi encontrado a entidade de PerfilEmail de GUID = {guid_perfil_email}"
            )

        # Deleta a entidade no banco de dados
        return await self.perfil_repo.delete_email_profile(
            guid_perfil_email,
        )

    async def insert_phone_profile_by_guid_usuario(
        self, guid_usuario: str, perfil_phone_input: PerfilPhonePostInput
    ):

        # Procurando o perfil a partir do guid do usu??rio
        perfil = await self.perfil_repo.find_profile_by_guid_usuario(
            guid_usuario,
            load_all_entities=False
        )
        if not perfil:
            raise exceptions.ProfileNotFoundException(
                detail=f"N??o foi encontrado um perfil para o usu??rio {guid_usuario}"
            )

        # Verificando se tipo_contato ?? v??lido
        id_tipo_contato = perfil_phone_input.id_tipo_contato
        tipo_contato = None

        if id_tipo_contato is not None:
            tipos_contato = await self.tipo_contato_repo.find_all_tipos_contato_by_filters(
                [TipoContato.id == id_tipo_contato]
            )
            if len(tipos_contato) == 0:
                raise exceptions.TipoContatoNotFoundException(
                    detail=f"N??o foi encontrado um tipo de contato com o ID = {id_tipo_contato}"
                )
            else:
                tipo_contato = tipos_contato[0]

        # Inserindo no banco de dados
        perfil_phone_dict = perfil_phone_input.convert_to_dict()
        perfil_phone_dict['id_perfil'] = perfil.id
        perfil = await self.perfil_repo.insert_phone_profile(perfil_phone_dict)
        return perfil

    async def patch_phone_profile_by_guid(
        self, guid_perfil_phone: str, perfil_phone_patch_input: PerfilPhonePatchInput
    ):

        # Procurando a entidade de PerfilPhone a partir do guid do perfil_phone
        perfil_phone = await self.perfil_repo.find_perfil_phone_by_guid(
            guid_perfil_phone
        )
        if not perfil_phone:
            raise exceptions.ProfilePhoneNotFoundException(
                detail=f"N??o foi encontrado a entidade de PerfilPhone de GUID = {guid_perfil_phone}"
            )

        # Verificando se o novo tipo_contato ?? v??lido
        id_tipo_contato = perfil_phone_patch_input.id_tipo_contato
        if id_tipo_contato is not None:
            tipos_contato = await self.tipo_contato_repo.find_all_tipos_contato_by_filters(
                [TipoContato.id == id_tipo_contato]
            )
            if len(tipos_contato) == 0:
                raise exceptions.TipoContatoNotFoundException(
                    detail=f"N??o foi encontrado um tipo de contato com o ID = {id_tipo_contato}"
                )

        # Inserindo no banco de dados
        perfil_phone_patch_dict = perfil_phone_patch_input.convert_to_dict()
        return await self.perfil_repo.atualiza_phone_profile(
            guid_perfil_phone,
            perfil_phone_patch_dict
        )

    async def delete_phone_profile_by_guid(
        self, guid_perfil_phone: str
    ):

        # Procurando a entidade de PerfilPhone a partir do guid do perfil_phone
        perfil_phone = await self.perfil_repo.find_perfil_phone_by_guid(
            guid_perfil_phone
        )
        if not perfil_phone:
            raise exceptions.ProfilePhoneNotFoundException(
                detail=f"N??o foi encontrado a entidade de PerfilPhone de GUID = {guid_perfil_phone}"
            )

        # Deleta a entidade no banco de dados
        return await self.perfil_repo.delete_phone_profile(
            guid_perfil_phone,
        )

    async def insert_profile(
        self, perfil_input: NotOwnerPerfilPostInput,
        usuario_input: UsuarioPostInput
    ):
        profile_dict = perfil_input.dict(exclude_unset=True)

        # Preenchendo nome exibi????o e normalizacao se existir
        nome_exibicao = profile_dict.get('nome_exibicao')
        profile_dict['nome_exibicao_normalized'] = (
            utils.normalize_string(nome_exibicao)
            if nome_exibicao
            else None
        )

        await self.usuario_repo.insere_usuario(usuario_input.dict())

        perfil = await self.perfil_repo.insere_perfil(profile_dict)

        return await self.perfil_repo.find_profile_by_guid(perfil.guid)

