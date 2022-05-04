"""
    Define as permissões do sistema que dependem das funções do usuário
"""


from enum import Enum


class RoleBasedPermission(Enum):

    ANY_OP = 'ANY_OP'

