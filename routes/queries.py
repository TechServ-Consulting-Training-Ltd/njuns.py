from typing import Optional

from ._base import BaseRoute
from ..route import Route
from ..utils import Response, MISSING


class QueriesRoute(BaseRoute):
    """Represents endpoints to the queries route"""

    async def fetch_queries(self, entity_name: str, /) -> Response:
        """Gets a list of queries.

        :param entity_name: Entity name.
        :type entity_name: str
        :return:
        """
        return await self.request(Route("GET", "/queries/{}".format(entity_name)))

    async def execute_query(
        self,
        entity_name: str,
        query_name: str,
        *,
        limit: Optional[int] = MISSING,
        offset: Optional[int] = MISSING,
        view: Optional[str] = MISSING,
        return_nulls: Optional[bool] = MISSING,
        return_count: Optional[bool] = MISSING,
        dynamic_attributes: Optional[bool] = MISSING,
    ) -> Response:
        """Executes a query and retrieve up to 50 results.

        :param entity_name: Entity name.
        :type entity_name: str
        :param query_name: Query name.
        :type query_name: str
        :param limit: Number of extracted entities. Max is capped to 50.
        :type limit: int
        :param offset: Position of the first result to retrieve
        :type offset: int
        :param view: Name of the view which is used for loading the entity. Specify this parameter if you want to
                    extract entities with the view other than it is defined in the REST queries configuration file.
        :type view: str
        :param return_nulls: Specifies whether null fields will be written to the result JSON
        :type return_nulls: bool
        :param return_count: Specifies whether the total count of entities should be returned in the 'X-Total-Count' header
        :type return_count: bool
        :param dynamic_attributes: Specifies whether entity dynamic attributes should be returned
        :type dynamic_attributes: bool
        :return: A list of entities is returned in the response body.
        """
        if isinstance(limit, int) and limit >= 50:
            raise ValueError("Limit must be less than or equal to 50")
        return await self.request(
            Route(
                "GET",
                "/queries/{}/{}".format(
                    entity_name,
                    query_name,
                )
                + Route.assemble_params(
                    limit=min(limit, 50) if isinstance(limit, int) else 50,
                    offset=offset if isinstance(offset, int) else MISSING,
                    view=view,
                    returnNulls=return_nulls,
                    returnCount=return_count,
                    dynamicAttributes=dynamic_attributes,
                ),
            )
        )
