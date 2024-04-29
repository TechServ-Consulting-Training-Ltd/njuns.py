import logging
from enum import Enum
from logging import Logger
from typing import Optional, Any, List, Union

from ._base import BaseRoute
from ..models.entity import Entity
from ..route import Route
from ..utils import MISSING, Response

_log: Logger = logging.getLogger(__name__)


class EntitySearchOperator(Enum):
    EQ = "="
    LTGT = "<>"
    LT = "<"
    LTEQ = "<="
    GT = ">"
    GTEQ = ">="
    STARTSWITH = "startsWith"
    ENDSWITH = "endsWith"
    CONTAINS = "contains"
    NOTEMPTY = "notEmpty"
    IN = "in"
    NOTIN = "notin"


class EntitySearchGroup(Enum):
    OR = "OR"
    AND = "AND"


class EntitySearchCondition:

    def __init__(
            self,
            _property: Optional[str] = MISSING,
            operator: Optional[EntitySearchOperator] = MISSING,
            value: Optional[Union[List[Any], str]] = MISSING,
            *,
            group: Optional[EntitySearchGroup] = None,
            conditions: Optional[List[Any]] = None,
    ):
        """A class instance of filter conditions for entity search.
        Note: If this is a condition group, property, operator, and value should not be specified.

        :param _property: The property name as the search key.
        :param operator: The operator used in this search condition. If the operator is "in" or "notIn" then the value should be a JSON array.
        :param value: The value for the search condition key.
        :param group: The condition's "OR" or "AND" grouping if needed.
        :param conditions: If this is a condition group, the child conditions should be specified here.
        """
        if group is EntitySearchGroup and (_property or operator or value):
            raise ValueError("Cannot specify both group and property/operator/value")

        if group is EntitySearchGroup and (conditions is None or len(conditions if conditions else [])) == 0:
            raise ValueError("Child conditions must be specified when grouping")

        if operator is EntitySearchOperator and not (operator == EntitySearchOperator.IN or operator == EntitySearchOperator.NOTIN) and value is not List:
            raise ValueError("Value must be a list when using 'in' or 'notin' operator")

        self.property: str = _property
        self.operator: EntitySearchOperator = operator
        self.value: Union[List[Any], str] = value
        self.group: Optional[EntitySearchGroup] = group
        self.conditions: Optional[List[EntitySearchCondition]] = conditions

    @property
    def as_dict(self) -> dict:
        """Get the dictionary representation of this :class:`EntitySearchGroup`.

        :return: A dictionary representation of this :class:`EntitySearchGroup`.
        """
        if self.group:
            return {
                "group": self.group.value,
                "conditions": list(map(lambda c: c.as_dict, self.conditions)),
            }
        else:
            return {
                "property": self.property,
                "operator": self.operator.value,
                "value": self.value,
            }


class EntitiesRoute(BaseRoute):
    """Represents endpoints to the entity route"""

    async def fetch_entities(
            self,
            entity_name: str,
            *,
            view: Optional[str] = MISSING,
            limit: Optional[int] = MISSING,
            offset: Optional[int] = MISSING,
            sort: Optional[str] = MISSING,
            return_nulls: Optional[bool] = MISSING,
            return_count: Optional[bool] = MISSING,
            dynamic_attributes: Optional[bool] = MISSING,
    ) -> List[Entity]:
        """Gets a list of entities, up to 50.

        Entities are found in the data model descriptions under "Help -> Data Model -> Known entities" after logging in.

        :param entity_name: Entity name.
        :type entity_name: str
        :param view: Name of the view which is used for loading the entity.
        :type view: str
        :param limit: Number of extracted entities. The max is capped at 50.
        :type limit: int
        :param offset: Position of the first result to retrieve.
        :type offset: int
        :param sort: Name of the field to be sorted by. If the name is preceding by the '+' character, then
                the sort order is ascending, if by the '-' character then descending. If there is no special
                character before the property name, then ascending sort will be used.
        :type sort: str
        :param return_nulls: Specifies whether null fields will be written to the result JSON.
        :type return_nulls: bool
        :param return_count: Specifies whether the total count of entities should be returned in the 'X-Total-Count' header.
        :type return_count: bool
        :param dynamic_attributes: Specifies whether entity dynamic attributes should be returned.
        :type dynamic_attributes: bool
        :return:
        """
        if isinstance(limit, int) and limit > 50:
            raise ValueError("Limit must be less than or equal to 50")
        return list(
            map(
                lambda e: Entity(**e),
                await self.request(
                    Route(
                        "GET",
                        "/entities/{}".format(entity_name)
                        + Route.assemble_params(
                            limit=min(limit, 50) if isinstance(limit, int) else MISSING,
                            offset=offset if isinstance(offset, int) else MISSING,
                            view=view,
                            sort=sort,
                            returnNulls=return_nulls,
                            returnCount=return_count,
                            dynamicAttributes=dynamic_attributes,
                        ),
                    )
                ),
            )
        )

    async def fetch_entity(
            self,
            entity_name: str,
            entity_id: str,
            *,
            view: Optional[str] = MISSING,
            dynamic_attributes: Optional[bool] = MISSING,
    ):
        """Fetch a single entity by UUID

        :param entity_name: The name of the entity type to fetch.
        :type entity_name: str
        :param entity_id: The UUID of the entity to fetch.
        :type entity_id: str
        :param view: The name of the view to use for loading the entity fields.
        :type view: str
        :param dynamic_attributes: Specifies whether entity dynamic attributes should be returned.
        :type dynamic_attributes: bool
        :return:
        """
        return Entity(
            **await self.request(
                Route(
                    "GET",
                    "/entities/{}/{}".format(entity_name, entity_id)
                    + Route.assemble_params(
                        view=view, dynamicAttributes=dynamic_attributes
                    ),
                )
            )
        )

    async def search_entities(
            self,
            entity_name: str,
            conditions: List[EntitySearchCondition],
            *,
            view: Optional[str] = MISSING,
            limit: Optional[int] = MISSING,
            offset: Optional[int] = MISSING,
            sort: Optional[str] = MISSING,
            return_nulls: Optional[bool] = MISSING,
            return_count: Optional[bool] = MISSING,
            dynamic_attributes: Optional[bool] = MISSING,
    ) -> List[Entity]:
        """Search for a list of entities, up to 50.

        Entities are found in the data model descriptions under "Help -> Data Model -> Known entities" after logging in.

        :param entity_name: Entity name.
        :type entity_name: str
        :param conditions: The conditions to use while searching.
        :type conditions: List[EntitySearchCondition]
        :param view: Name of the view which is used for loading the entity.
        :type view: str
        :param limit: Number of extracted entities. The max is capped at 50.
        :type limit: int
        :param offset: Position of the first result to retrieve.
        :type offset: int
        :param sort: Name of the field to be sorted by. If the name is preceding by the '+' character, then
                the sort order is ascending, if by the '-' character then descending. If there is no special
                character before the property name, then ascending sort will be used.
        :type sort: str
        :param return_nulls: Specifies whether null fields will be written to the result JSON.
        :type return_nulls: bool
        :param return_count: Specifies whether the total count of entities should be returned in the 'X-Total-Count' header.
        :type return_count: bool
        :param dynamic_attributes: Specifies whether entity dynamic attributes should be returned.
        :type dynamic_attributes: bool
        :return:
        """
        if isinstance(limit, int) and limit > 50:
            raise ValueError("Limit must be less than or equal to 50")

        json: dict = {
            "filter": {"conditions": list(map(lambda e: e.as_dict, conditions))},
        }

        if isinstance(limit, int):
            json["limit"] = min(limit, 50)
        if isinstance(offset, int):
            json["offset"] = offset
        if view:
            json["view"] = view
        if sort:
            json["sort"] = sort
        if return_nulls:
            json["nulls"] = return_nulls
        if return_count:
            json["count"] = return_count
        if dynamic_attributes:
            json["dynamicAttributes"] = dynamic_attributes

        return list(
            map(
                lambda e: Entity(**e),
                await self.request(
                    Route("POST", "/entities/{}/search".format(entity_name)), json=json
                ),
            )
        )

    async def create_entity(self, entity_name: str, *, entity: Entity) -> Response:
        """Creates new entity. The method expects a JSON with entity object in the request body. The entity object
        may contain references to other entities. These references are processed according to the following rules:

        - If the entity property is annotated with @Composition in the entity java class, then it will be saved with the main entity.
        - Otherwise a referenced entity with the given id will be searched. If it is found then the saved entity will have a reference to it.
          Otherwise, a response with code 400 will be returned.

        :param entity_name: Entity name.
        :type entity_name: str
        :param entity: The entity to be created.
        :type entity: Entity
        """
        return await self.request(Route("POST", "/entities/{}".format(entity_name)), json=entity.json)
