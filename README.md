# NJUNS API Wrapper Structure

This API wrapper tries to follow the design pattern of many other popular asynchronous Python API wrappers.
You first instantiate the [`NJUNSClient`](./client.py) class, call the [`NJUNSClient.login`](./client.py)
coroutine in an async loop, then call your desired async operations.

## Overview

- [`NJUNSClient`](client.py) - The main API client class that users should use. It handles requests and the session. It also
  subclasses [`HTTPClient`](http.py)
- [`HTTPClient`](http.py) - The main HTTP handler. Subclasses route classes to expose their methods to [`NJUNSClient`](./client.py) and provides its `self`
  instance to each route to provide localized access to
  the [`aiohttp.ClientSession`](https://docs.aiohttp.org/en/stable/client_reference.html#aiohttp.ClientSession) instance.
- **Models**:
    - [`Route`](route.py) - Represents a full path to the API. The environment (UAT or prod) can be set while instantiating the [`NJUNSClient`](client.py).
      There is also a static helper method that will assemble non-[`MISSING`](utils.py) key-value pairs into a partial URL string that can be appended to a base
      URL.
    - [`MISSING`](utils.py) - A sentinel value that represents a non-optional value that can be missing. Equivalent to a late initialized attribute.
    - [`Entity`](models/entity.py) - A class representing an entity retrieved from the API. Entities seem to be designed as modular so this implementation
      follows that design. The class base attributes are the entity ID, entity name, and instance name. At initialization, the `__dict__` is dynamically updated
      to provide other attributes available within the actual entity received.
    - [`PredefinedQuery`](models/predefined_query.py) - This class represents a stored, predefined query. This contains the query name,
      the [JPQL](https://docs.oracle.com/cd/E11035_01/kodo41/full/html/ejb3_langref.html) query, the entity name, view name,
      and [`QueryParameter`](models/predefined_query.py)'s present.
    - [`UserInfo`](models/user.py) - A class representing the currently logged-in user. The [`NJUNSClient`](client.py) instance will fetch the current user and
      populate the [`NJUNSClient.user_info`](client.py) field on login.
- **Routes**:
    - [`BaseRoute`](routes/_base.py) - The base route abstract class. This should not be instantiated, only subclassed. It provides route classes with
      the `client` instance so that they can initiate requests from the single `aiohttp` client session. As such, this class has no abstract methods or
      properties aside from exposing [`HTTPClient`](http.py).
    - [`EntitiesRoute`](routes/entities.py) - Contains endpoints and helper methods to request operations on the entities route.
      Subclasses [`BaseRoute`](routes/_base.py) and its implementer is [`HTTPClient`](http.py) to expose its methods to [`NJUNSClient`](client.py).
    - [`QueriesRoute`](routes/queries.py) - Contains endpoints and helper methods to request operations on the queries route.
      Subclasses [`BaseRoute`](routes/_base.py) and its implementer is [`HTTPClient`](http.py) to expose its methods to [`NJUNSClient`](client.py).
- **Exceptions**:
    - [`HTTPException`](exceptions.py) - The "base" exception for this library. Contains information about the route, the message provided to the exception, the
      response (if any), and the response content (as
      retrieving [`aiohttp.ClientResponse`](https://docs.aiohttp.org/en/stable/client_reference.html#aiohttp.ClientResponse) content asynchronously cannot be
      done in the `__init__` method)
    - [`AuthenticationException`](exceptions.py) - Raised when an HTTP request failed while authenticating.
    - [`ServerError`](exceptions.py) - Raised when an HTTP request returns a 500 status code
    - [`Forbidden`](exceptions.py) - Raised when an HTTP request returned a 403 status code.
    - [`NotFound`](exceptions.py) - Raised when an HTTP request returns a 404 status code.
