from typing import Dict, Any


class Entity:
    """A class representing an entity. More can be found after logging in to NJUNS -> Help -> Data Model"""

    def __init__(self, *_, **kwargs):
        self.id = kwargs.get("id")
        self.entity_name = kwargs.get("_entity_name")
        self.instance_name = kwargs.get("_instance_name")
        self.__dict__.update(kwargs)

    # @classmethod
    # def build(cls, *_, **kwargs) -> "Entity":
    #     """
    #     Factory constructor to build an entity to be sent in a POST request.
    #     """
    #     entity = cls(**kwargs)
    #     del entity.id
    #     del entity.entity_name
    #     del entity.instance_name
    #     return entity

    def __getattr__(self, name):
        if name in self.__dict__:
            return self.__dict__[name]
        else:
            raise AttributeError(name=name)

    def __setattr__(self, key, value):
        self.__dict__[key] = value

    @property
    def json(self) -> Dict[str, Any]:
        return self.__dict__
