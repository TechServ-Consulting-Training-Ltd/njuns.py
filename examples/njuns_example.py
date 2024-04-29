import asyncio
import logging
import os
from pprint import pprint

from njuns.routes.entities import EntitySearchGroup
from njuns import NJUNSClient, EntitySearchCondition, EntitySearchOperator

# Instantiate the client
client = NJUNSClient(log_level=logging.ERROR)


async def main():
    # Login with credentials, use prod environment
    await client.login(username=os.getenv("USERNAME").strip(), password=os.getenv("PASSWORD").strip(), use_uat_environment=False)

    # Fetch an entity by searching for its ticket number
    entity = (
        await client.search_entities(
            entity_name="njuns$Ticket", conditions=[EntitySearchCondition("ticketNumber", EntitySearchOperator.EQ, "5928019")], view="_minimal"
        )
    )[0]

    pprint(entity.ticketId)

    # Get the ticket's wall entries
    wall = await client.search_entities(
        entity_name="njuns$TicketWallEntry",
        conditions=[
            EntitySearchCondition(
                group=EntitySearchGroup.AND,
                conditions=[
                    EntitySearchCondition("ticket", EntitySearchOperator.EQ, entity.id),
                    EntitySearchCondition("type", EntitySearchOperator.EQ, "ACTION"),
                ],
            )
        ],
        view="ticketWallEntry-browse-view",
    )

    pprint(list(map(lambda e: f"{e['comment']} -> {e['createTs']}", map(lambda a: a.__dict__, wall))))

    # Close the client and cleanup
    await client.close()


asyncio.run(main())
