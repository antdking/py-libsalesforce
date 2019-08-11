from .interface import IQueryClient, IQueryManager, IQueryModel
from .manager import QueryManager


def get_query_manager(model: IQueryModel, client: IQueryClient) -> IQueryManager:
    return QueryManager(model.name, client)
