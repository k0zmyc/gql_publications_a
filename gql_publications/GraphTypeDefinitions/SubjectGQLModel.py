from typing import List, Union, Annotated, Optional
import strawberry as strawberryA
import datetime
import typing
import uuid
import strawberry
from gql_publications.utils.Dataloaders import getLoadersFromInfo, getUserFromInfo
from .BaseGQLModel import BaseGQLModel


from ._GraphResolvers import (
    resolve_id,

    resolve_valid,

    resolve_created,
    resolve_lastchange,
    resolve_createdby,
    resolve_changedby,
    #resolve_rbacobject,

    createRootResolver_by_id
)

#from gql_publications.GraphTypeDefinitions._GraphPermissions import RoleBasedPermission, OnlyForAuthentized

PublicationGQLModel = Annotated["PublicationGQLModel", strawberryA.lazy(".PublicationGQLModel")]

@strawberryA.federation.type(
    keys=["id"], 
    description="""Entity representing a publication subject"""
)
class SubjectGQLModel(BaseGQLModel):
    @classmethod
    def getLoader(cls, info):
        return getLoadersFromInfo(info).publicationsubjects

    id = resolve_id

    valid = resolve_valid

    created = resolve_created
    lastchange = resolve_lastchange
    createdby = resolve_createdby
    changedby = resolve_changedby
    #rbacobject = resolve_rbacobject

    @strawberryA.field(description="""Publication ID""")
    async def publication_id(self, info: strawberryA.types.Info) -> Optional ["PublicationGQLModel"]:
        from .PublicationGQLModel import PublicationGQLModel  # Import here to avoid circular dependency
        result = await PublicationGQLModel.resolve_reference(info, self.publication_id)
        return result
    
    
###########################################################################################################################
#                                                                                                                         #
#                                                       Query                                                             #
#                                                                                                                         #
###########################################################################################################################

from contextlib import asynccontextmanager

from dataclasses import dataclass
from .utils import createInputs
@createInputs
@dataclass
class SubjectWhereFilter:
    id: uuid.UUID
    #subject_id: uuid.UUID
    publication_id: uuid.UUID
    valid: bool
    
    createdby: uuid.UUID
    changedby: uuid.UUID


@strawberryA.field(description="""Returns a list of publication subjects""")
async def subject_page(
    self, info: strawberryA.types.Info, skip: int = 0, limit: int = 10,
    where: Optional[SubjectWhereFilter] = None
) -> List[SubjectGQLModel]:
    loader = getLoadersFromInfo(info).publicationsubjects
    wf = None if where is None else strawberry.asdict(where)
    result = await loader.page(skip, limit, where = wf)
    return result


subject_by_id = createRootResolver_by_id(SubjectGQLModel, description="Returns subject by its id")

###########################################################################################################################
#                                                                                                                         #
#                                                       Models                                                            #
#                                                                                                                         #
###########################################################################################################################

from typing import Optional

@strawberryA.input(description="Definition of a subject used for creation")
class SubjectInsertGQLModel:
    publication_id: uuid.UUID = strawberryA.field(description="The ID of the publication")
    subject_id: uuid.UUID = strawberryA.field(description="The ID of the subject")
    
    valid: Optional[bool] = strawberryA.field(description="Indicates whether the subjects data is valid or not (optional)", default=True)
    id: Optional[uuid.UUID] = strawberryA.field(description="The ID of the publication subject", default=None)
    content_id: Optional[uuid.UUID] = strawberryA.field(description="The ID of the content associated with the subject ", default=None)
    createdby: strawberry.Private[uuid.UUID] = None
    rbacobject: strawberry.Private[uuid.UUID] = None
    
@strawberryA.input(description="Definition of a subject used for update")
class SubjectUpdateGQLModel:
    id: uuid.UUID = strawberryA.field(description="The ID of the subject")
    lastchange: datetime.datetime = strawberry.field(description="Timestamp of last change")

    valid: Optional[bool] = strawberryA.field(description="Indicates whether the subjects data is valid or not", default=None)
    subject_id: Optional[uuid.UUID] = strawberryA.field(description="The ID of the subject type",default=None)
    changedby: strawberry.Private[uuid.UUID] = None

@strawberryA.type(description="Result of a mutation for a subject")
class SubjectResultGQLModel:
    id: uuid.UUID = strawberryA.field(description="The ID of the subject", default=None)
    msg: str = strawberryA.field(description="Result of the operation (OK/Fail)", default=None)

    @strawberryA.field(description="Returns the subject")
    async def subject(self, info: strawberryA.types.Info) -> Union[SubjectGQLModel, None]:
        result = await SubjectGQLModel.resolve_reference(info, self.id)
        return result


###########################################################################################################################
#                                                                                                                         #
#                                                       Mutations                                                         #
#                                                                                                                         #
###########################################################################################################################

@strawberryA.mutation(description="Adds a new subject.")
async def subject_insert(self, info: strawberryA.types.Info, subject: SubjectInsertGQLModel) -> SubjectResultGQLModel:
    user = getUserFromInfo(info)
    subject.createdby = uuid.UUID(user["id"])
    loader = getLoadersFromInfo(info).publicationsubjects
    row = await loader.insert(subject)
    result = SubjectResultGQLModel()
    result.msg = "ok"
    result.id = row.id
    return result

@strawberryA.mutation(description="Update the subject.")
async def subject_update(self, info: strawberryA.types.Info, subject: SubjectUpdateGQLModel) -> SubjectResultGQLModel:
    user = getUserFromInfo(info)
    subject.changedby = uuid.UUID(user["id"])
    loader = getLoadersFromInfo(info).publicationsubjects
    row = await loader.update(subject)
    result = SubjectResultGQLModel()
    result.msg = "ok"
    result.id = subject.id
    result.msg = "ok" if (row is not None) else "fail"
    return result


@strawberry.mutation(
    description="Delete the publication.")
async def subject_delete(self, info: strawberryA.types.Info, id:uuid.UUID, 
    lastchange: datetime.datetime = strawberry.field()) -> SubjectResultGQLModel:
    loader = getLoadersFromInfo(info).publicationsubjects
    row = await loader.delete(id=id)
    result = SubjectResultGQLModel(id=id, msg="ok")
    result.msg = "fail" if row is None else "ok"
    return result