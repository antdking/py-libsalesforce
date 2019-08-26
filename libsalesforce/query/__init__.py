from .api import get_query_manager, get_filter_builder

__all__ = ("get_query_manager", "get_filter_builder")


"""
from libsalesforce.client import Client
from libsalesforce.model import NamedModel
from libsalesforce.query import *
client = Client()
Opportunity = NamedModel('Opportunity')
qm = get_query_manager(Opportunity, client)
O = get_filter_builder()
A = get_filter_builder()

opportunities = qm.run(
    {
        'id': o.Id,
        'accounts': [
            {'id': a.Id}
            for a in o.Accounts(where=
                (A.Id == "dfvfdbvdfv")
            )
        ]
    }
    for o in qm(where=
        (O.Id == "hio")
    )
)
"""
