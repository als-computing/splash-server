from splash.resource.base import SingleObjectResource, MultiObjectResource


class Users(MultiObjectResource):
    def __init__(self, service):
        super().__init__(service)


class User(SingleObjectResource):
    def __init__(self, service):
        super().__init__(service)
