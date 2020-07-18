from splash.resource.base import SingleObjectResource, MultiObjectResource


class Compounds(MultiObjectResource):
    def __init__(self, service):
        super().__init__(service)


class Compound(SingleObjectResource):
    def __init__(self, service):
        super().__init__(service)