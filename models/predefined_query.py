from typing import List


class PredefinedQuery:
    """A class representing a query"""

    def __init__(self, *_, **kwargs):
        self.name: str = kwargs.get("name")
        self.jpql: str = kwargs.get("jpql")
        self.entityName: str = kwargs.get("entityName")
        self.viewName: str = kwargs.get("viewName")
        self.params: List[QueryParameter] = list(
            map(lambda x: QueryParameter(**x), kwargs.get("params", []))
        )


class QueryParameter:
    """A class representing a query parameter"""

    def __init__(self, *_, **kwargs):
        self.description: str = kwargs.get("description")
        self.name: str = kwargs.get("name")
        self.type: str = kwargs.get("type")
