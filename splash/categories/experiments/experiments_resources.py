from splash.resource.base import SingleObjectResource, MultiObjectResource


class Experiments(MultiObjectResource):
    def __init__(self, service):
        super().__init__(service)


class Experiment(SingleObjectResource):
    def __init__(self, service):
        super().__init__(service)
