from .interface import IQueryClient, IQueryManager, IQueryModel
from .manager import QueryManager
from .filter import FilterBuilder


def get_query_manager(model: IQueryModel, client: IQueryClient) -> IQueryManager:
    return QueryManager(model.name, client)


def get_filter_builder():
    return FilterBuilder()
