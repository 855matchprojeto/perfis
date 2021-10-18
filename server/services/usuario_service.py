from server.schemas.usuario_schema import CurrentUserOutput


class UsuarioService:

    @staticmethod
    def current_user_output(current_user):
        """
            Converte o current_user para uma versão
            sem exposição de dados confidenciais como
            funções e permissões
        """
        return CurrentUserOutput(**current_user.dict())

