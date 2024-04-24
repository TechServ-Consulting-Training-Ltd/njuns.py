# NJUNS API
To gain access to the NJUNS API, you must request access from aweaver [AT] njuns [DOT] com as stated in their FAQ. 
For testing purposes, it would be ideal to also request access to their test UAT environment as well. These are separate credentials.

Once this process is complete, you may send a token request either using the Postman examples NJUNS provides, or with this request 
(substitute USERNAME and PASSWORD with your credentials):
```http request
POST /{APP}/rest/v2/oauth/token/grant_type=password&username={USERNAME}&password={PASSWORD} HTTP/1.1
Host: {DOMAIN}.njuns.com
Content-Type: application/x-www-form-urlencoded
Authorization: Basic Y2xpZW50OnNlY3JldA==

```
```shell
curl -X POST \
  -H "Authorization: Basic Y2xpZW50OnNlY3JldA==" \
  -H "Content-Type: application/x-www-form-urlencoded" \
  "https://{DOMAIN}.njuns.com/{APP}/rest/v2/oauth/token/grant_type=password&username={USERNAME}&password={PASSWORD}"
```

## Using the NJUNS package
```
# Install via pip
pip install git+https://github.com/TechServ-Consulting-Training-Ltd/njuns.py
```

> [!NOTE]
> Because of the large amounts of entity types and their data,
> this library will dynamically set class attributes for `Entity`.
> When you attempt to access an attribute, your IDE may warn you
> that the attribute reference is unresolved. If you are certain
> that the attribute is present in the API response, this should be 
> fine to ignore. To troubleshoot this, instantiate the client
> with a `log_level` of `logging.DEBUG` and inspect the API
> response.

```py
# Import the API client
import asyncio

from njuns import NJUNSClient

# Instantiate the client
client = NJUNSClient()


# Define your main coroutine
async def main():
    # Login with your API credentials
    await client.login(username="email", password="password")

    # Print your user info
    print(client.user_info.name)

    # Fetch five entities
    entities = await client.fetch_entities(entity_name="njuns$Ticket", limit=5)

    # Print the contact email of the first ticket entity
    print(entities[0].contactEmail)


# Run the coroutine
asyncio.run(main())
```

# NJUNS API Wrapper Structure

This API wrapper tries to follow the design pattern of many other popular asynchronous Python API wrappers.
You first instantiate the [`NJUNSClient`](./client.py) class, call the [`NJUNSClient.login`](./client.py)
coroutine in an async loop, then call your desired async operations.

## Overview

- [`NJUNSClient`](njuns/client.py) - The main API client class that users should use. It handles requests and the session. It also
  subclasses [`HTTPClient`](njuns/http.py)
- [`HTTPClient`](njuns/http.py) - The main HTTP handler. Subclasses route classes to expose their methods to [`NJUNSClient`](njuns/client.py) and provides its `self`
  instance to each route to provide localized access to
  the [`aiohttp.ClientSession`](https://docs.aiohttp.org/en/stable/client_reference.html#aiohttp.ClientSession) instance.
- **Models**:
    - [`Route`](njuns/route.py) - Represents a full path to the API. The environment (UAT or prod) can be set while instantiating the [`NJUNSClient`](njuns/client.py).
      There is also a static helper method that will assemble non-[`MISSING`](njuns/utils.py) key-value pairs into a partial URL string that can be appended to a base
      URL.
    - [`MISSING`](njuns/utils.py) - A sentinel value that represents a non-optional value that can be missing. Equivalent to a late initialized attribute.
    - [`Entity`](njuns/models/entity.py) - A class representing an entity retrieved from the API. Entities seem to be designed as modular so this implementation
      follows that design. The class base attributes are the entity ID, entity name, and instance name. At initialization, the `__dict__` is dynamically updated
      to provide other attributes available within the actual entity received.
    - [`PredefinedQuery`](njuns/models/predefined_query.py) - This class represents a stored, predefined query. This contains the query name,
      the [JPQL](https://docs.oracle.com/cd/E11035_01/kodo41/full/html/ejb3_langref.html) query, the entity name, view name,
      and [`QueryParameter`](models/predefined_query.py)'s present.
    - [`UserInfo`](njuns/models/user.py) - A class representing the currently logged-in user. The [`NJUNSClient`](njuns/client.py) instance will fetch the current user and
      populate the [`NJUNSClient.user_info`](njuns/client.py) field on login.
- **Routes**:
    - [`BaseRoute`](njuns/routes/_base.py) - The base route abstract class. This should not be instantiated, only subclassed. It provides route classes with
      the `client` instance so that they can initiate requests from the single `aiohttp` client session. As such, this class has no abstract methods or
      properties aside from exposing [`HTTPClient`](njuns/http.py).
    - [`EntitiesRoute`](njuns/routes/entities.py) - Contains endpoints and helper methods to request operations on the entities route.
      Subclasses [`BaseRoute`](njuns/routes/_base.py) and its implementer is [`HTTPClient`](njuns/http.py) to expose its methods to [`NJUNSClient`](njuns/client.py).
    - [`QueriesRoute`](njuns/routes/queries.py) - Contains endpoints and helper methods to request operations on the queries route.
      Subclasses [`BaseRoute`](njuns/routes/_base.py) and its implementer is [`HTTPClient`](njuns/http.py) to expose its methods to [`NJUNSClient`](njuns/client.py).
- **Exceptions**:
    - [`HTTPException`](njuns/exceptions.py) - The "base" exception for this library. Contains information about the route, the message provided to the exception, the
      response (if any), and the response content (as
      retrieving [`aiohttp.ClientResponse`](https://docs.aiohttp.org/en/stable/client_reference.html#aiohttp.ClientResponse) content asynchronously cannot be
      done in the `__init__` method)
    - [`AuthenticationException`](njuns/exceptions.py) - Raised when an HTTP request failed while authenticating.
    - [`ServerError`](njuns/exceptions.py) - Raised when an HTTP request returns a 500 status code
    - [`Forbidden`](njuns/exceptions.py) - Raised when an HTTP request returned a 403 status code.
    - [`NotFound`](njuns/exceptions.py) - Raised when an HTTP request returns a 404 status code.
