import logging
from logging import Logger
from typing import List
from uuid import UUID

from ._base import BaseRoute
from ..route import Route
from ..utils import Response

_log: Logger = logging.getLogger(__name__)


class ServicesRoute(BaseRoute):
    """Represents endpoints to the services route."""

    async def post_comment_to_ticket(
            self,
            *,
            ticket_id: UUID,
            comment: str,
            file_descriptor_ids: List[UUID] = (),
            flagged: bool = False
    ) -> Response:
        return await self.request(Route(
            "GET",
            "/services/njuns_TicketService/addPosting"
            + Route.assemble_params(
                ticketId=ticket_id,
                comment=comment,
                fileDescriptorIds=f"[{",".join([str(i) for i in file_descriptor_ids])}]",
                isFlagged=flagged
            )
        ))
