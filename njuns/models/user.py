class UserInfo:
    """A class representing the currently logged-in user."""

    def __init__(self, *_, **kwargs):
        self.id: str = kwargs.get("id")
        self.login: str = kwargs.get("login")
        self.name: str = kwargs.get("name")
        self.firstName: str = kwargs.get("firstName")
        self.middleName: str = kwargs.get("middleName")
        self.lastName: str = kwargs.get("lastName")
        self.position: str = kwargs.get("position")
        self.email: str = kwargs.get("email")
        self.timeZone: str = kwargs.get("timeZone")
        self.language: str = kwargs.get("language")
        self.locale: str = kwargs.get("locale")
        self._instanceName: str = kwargs.get("_instanceName")
