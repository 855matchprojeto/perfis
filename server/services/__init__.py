"""
    Módulo entre o controller e o repository
    É responsável pela lógica dos endpoints usando o banco de dados
    de maneira abstrata, a partir da camada repository
"""


def insert_filter(filter_dict_to_insert, filter_dict_to_append):
    for model in filter_dict_to_append:
        if model not in filter_dict_to_insert:
            filter_dict_to_insert[model] = []
        filter_dict_to_insert[model].append(filter_dict_to_append[model])


def get_filters_base(params_dict: dict, filter_factory):
    filters = []
    filter_factory = filter_factory.get_filter_factory()
    for key in params_dict.keys():
        param_payload = params_dict[key]
        if param_payload:
            filters.append(filter_factory[key](param_payload))
    return filters
