from .paginators import BasePaginator


class BaseMenu(BasePaginator):

    def __init__(self, ctx):
        super().__init__(ctx)
