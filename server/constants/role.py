"""
    Define as funções dos usuários do sistema.
    É especialmente útil para definir os scopes do token de acesso
"""


class Role:

    ADMIN = {
        "name": "ADMIN",
        "description": "Usuário com acesso administrativo"
    }

    @staticmethod
    def get_all_roles_list():
        return [
            Role.ADMIN
        ]

    @staticmethod
    def get_all_roles_dict():
        all_roles_dict = {}
        for role_dict in Role.get_all_roles_list():
            all_roles_dict.update({role_dict['name']: role_dict['description']})
        return all_roles_dict


