from typing import List, Union, Annotated, Optional
import typing
from unittest import result
import strawberry as strawberryA
import uuid
from contextlib import asynccontextmanager

@asynccontextmanager
async def withInfo(info):
    asyncSessionMaker = info.context["asyncSessionMaker"]
    async with asyncSessionMaker() as session:
        try:
            yield session
        finally:
            pass


import datetime

from gql_publications.utils.DBFeeder import randomDataStructure

from gql_publications.GraphResolvers import (
    resolvePublicationById
)
from gql_publications.GraphResolvers import (
    resolvePublicationTypeById,
    resolveAuthorsForPublication
)

AuthorGQLModel = Annotated["AuthorGQLModel", strawberryA.lazy(".AuthorGQLModel")]
PublicationEditorGQLModel = Annotated["PublicationEditorGQLModel", strawberryA.lazy(".PublicationEditorGQLModel")]
PublicationTypeGQLModel = Annotated["PublicationTypeGQLModel", strawberryA.lazy(".PublicationTypeGQLModel")]


@strawberryA.federation.type(
    keys=["id"], description="""Entity representing a publication"""
)

class PublicationGQLModel:
    @classmethod
    async def resolve_reference(cls, info: strawberryA.types.Info, id: uuid.UUID):
        async with withInfo(info) as session:
            result = await resolvePublicationById(session, id)
            result._type_definition = cls._type_definition  # little hack :)
            return result

    @strawberryA.field(description="""primary key""")
    def id(self) -> uuid.UUID:
        return self.id

    @strawberryA.field(description="""Timestamp""")
    def lastchange(self) -> datetime.datetime:
        return self.lastchange

    @strawberryA.field(description="""name""")
    def name(self) -> str:
        return self.name

    @strawberryA.field(description="""published year""")
    def published_date(self) -> datetime.date:
        return self.published_date

    @strawberryA.field(description="""place""")
    def place(self) -> str:
        return self.place

    @strawberryA.field(description="""reference""")
    def reference(self) -> str:
        return self.reference

    @strawberryA.field(description="""If a publication is valid""")
    def valid(self) -> bool:
        return self.valid

    @strawberryA.field(description="""last change""")
    def lastchange(self) -> datetime.datetime:
        return self.lastchange

    @strawberryA.field(
        description="""List of authors, where the author participated in publication"""
    )
    async def authors(
        self, info: strawberryA.types.Info
    ) -> typing.List["AuthorGQLModel"]:
        async with withInfo(info) as session:
            result = await resolveAuthorsForPublication(session, self.id)
            return result

    @strawberryA.field(description="""Publication type""")
    async def publicationtype(
        self, info: strawberryA.types.Info
    ) -> PublicationTypeGQLModel:
        async with withInfo(info) as session:
            result = await resolvePublicationTypeById(session, self.publication_type_id)
            return result

    @strawberryA.field(description="""returns the publication editor if possible""")
    async def editor(
        self, info: strawberryA.types.Info
    ) -> Union["PublicationEditorGQLModel", None]:
        ## current user must be checked if has rights to get the editor
        ## if not, then None value must be returned
        return self
    

    
@strawberryA.input
class PublicationInsertGQLModel:
    name: str
    
    id: Optional[uuid.UUID] = None
    publication_type_id: Optional[uuid.UUID] = None
    place: Optional[str] = ""
    published_date: Optional[datetime.datetime] = datetime.datetime.now()
    reference: Optional[str] = ""
    valid: Optional[bool] = True




@strawberryA.type
class PublicationResultGQLModel:
    id: uuid.UUID = None
    msg: str = None

    @strawberryA.field(description="""Result of publication operation""")
    async def publication(self, info: strawberryA.types.Info) -> Union[PublicationGQLModel, None]:
        from .PublicationGQLModel import PublicationGQLModel
        result = await PublicationGQLModel.resolve_reference(info, self.id)
        return result
   


@strawberryA.input
class PublicationUpdateGQLModel:
    lastchange: datetime.datetime
    id: uuid.UUID

    name: Optional[str] = None
    publication_type_id: Optional[uuid.UUID] = None
    place: Optional[str] = None
    published_date: Optional[datetime.datetime] = None
    reference: Optional[str] = None
    valid: Optional[bool] = None