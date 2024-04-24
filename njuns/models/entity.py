class Entity:
    """A class representing an entity. More can be found after logging in to NJUNS -> Help -> Data Model"""

    def __init__(self, *_, **kwargs):
        self.id = kwargs.get("id")
        self.entity_name = kwargs.get("_entity_name")
        self.instance_name = kwargs.get("_instance_name")
        self.__dict__.update(kwargs)

    def __getattr__(self, name):
        if name in self.__dict__:
            return self.__dict__[name]
        else:
            raise AttributeError(name=name)
