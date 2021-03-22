from typing import Generator
from . import Page, NewPage, UpdatePage
from ..service.base import VersionedMongoService
from ..users import User


class PagesService(VersionedMongoService):

    def __init__(self, db, collection_name, versioned_collection_name):
        super().__init__(db, collection_name, versioned_collection_name)

    def create(self, current_user: User, page: NewPage) -> str:
        return super().create(current_user, page.dict())

    def retrieve_one(self, current_user: User, uid: str) -> Page:
        Page_dict = super().retrieve_one(current_user, uid)
        if Page_dict is None:
            return None
        return Page(**Page_dict)

    def retrieve_version(self, current_user: User, uid: str, version):
        return super().retrieve_version(current_user, uid, version)

    def get_num_versions(self, current_user, uid):
        return super().get_num_versions(current_user, uid)

    def retrieve_multiple(self,
                          current_user: User,
                          page: int = 1,
                          query=None,
                          page_size=10) -> Generator[Page, None, None]:
        cursor = super().retrieve_multiple(current_user, page, query, page_size, sort="title", order=1)
        for page_dict in cursor:
            yield Page(**page_dict)

    def retrieve_by_page_type(self,
                              current_user: User,
                              page_type: str,
                              page: int = 1,
                              page_size=10):
        query = {'page_type': page_type}
        return self.retrieve_multiple(current_user, page, query, page_size)

    def update(self, current_user: User, data: UpdatePage, uid: str, etag: str = None):
        return super().update(current_user, data.dict(), uid)

    def delete(self, current_user: User, uid):
        raise NotImplementedError

    def get_user_pages(self, request_user: User, uid: str):
        # find Pages that contain the member by uid
        query = {
            "members." + uid: {"$exists": True}
        }
        pages_dicts = list(self.retrieve_multiple(request_user, page=1, query=query))
        for page_dict in pages_dicts:
            yield Page(**page_dict)
