import strawberry
import uuid
import datetime
import typing
from typing import Optional
import logging

from inspect import signature
import inspect 
from functools import wraps
#from ._GraphPermissions import OnlyForAuthentized

UserGQLModel = typing.Annotated["UserGQLModel", strawberry.lazy(".externals")]

@strawberry.field(description="""Entity primary key"""", permission_classes=[OnlyForAuthentized()]")
def resolve_id(self) -> uuid.UUID:
    return self.id

@strawberry.field(description="""Time of last update""")
def resolve_lastchange(self) -> datetime.datetime:
    return self.lastchange

@strawberry.field(description="""Entity name """)
def resolve_name(self) -> str:
    return self.name

@strawberry.field(description="""Entity english name""")
def resolve_name_en(self) -> str:
    result = self.name_en if self.name_en else ""
    return result

@strawberry.field(description="""Entity order""")
def resolve_order(self) -> int:
    return self.order

@strawberry.field(description="""Entity share""")
def resolve_share(self) -> float:
    return self.share

@strawberry.field(description="""Entity reference - publication reference""")
def resolve_p_reference(self) -> str:
    return self.reference

@strawberry.field(description="""Published date""")
def resolve_date(self) -> datetime.datetime:
    return self.published_date

@strawberry.field(description="""Place of publishing""")
def resolve_place(self) -> str:
    return self.place

@strawberry.field(description="""Validity of event""")
def resolve_valid(self) -> bool:
    return self.valid

async def resolve_user(user_id):
    from .externals import UserGQLModel
    result = None if user_id is None else await UserGQLModel.resolve_reference(user_id)
    return result

@strawberry.field(description="""User ID """)
async def resolve_user_id(self) -> typing.Optional["UserGQLModel"]:
    return await resolve_user(self.user_id)

@strawberry.field(description="""Time of entity introduction""")
def resolve_created(self) -> typing.Optional[datetime.datetime]:
    return self.created


@strawberry.field(description="""Who created entity""")
async def resolve_createdby(self) -> typing.Optional["UserGQLModel"]:
    return await resolve_user(self.createdby)


@strawberry.field(description="""Who made last change""")
async def resolve_changedby(self) -> typing.Optional["UserGQLModel"]:
    return await resolve_user(self.changedby)


# RBACObjectGQLModel = typing.Annotated["RBACObjectGQLModel", strawberry.lazy(".externals")]
# @strawberry.field(description="""Who made last change""")
# async def resolve_rbacobject(self, info: strawberry.types.Info) -> typing.Optional[RBACObjectGQLModel]:
#     from .externals import RBACObjectGQLModel
#     result = None if self.rbacobject is None else await RBACObjectGQLModel.resolve_reference(info, self.rbacobject)
#     return result


resolve_result_id: uuid.UUID = strawberry.field(description="primary key of CU operation object")
resolve_result_msg: str = strawberry.field(description="""Should be `ok` if descired state has been reached, otherwise `fail`.
For update operation fail should be also stated when bad lastchange has been entered.""")

# fields for mutations insert and update
resolve_insert_id = strawberry.field(graphql_type=typing.Optional[uuid.UUID], description="primary key (UUID), could be client generated", default=None)
resolve_update_id = strawberry.field(graphql_type=uuid.UUID, description="primary key (UUID), identifies object of operation")
resolve_update_lastchage = strawberry.field(graphql_type=datetime.datetime, description="timestamp of last change = TOKEN")

# fields for mutation result
resolve_cu_result_id = strawberry.field(graphql_type=uuid.UUID, description="primary key of CU operation object")
resolve_cu_result_msg = strawberry.field(graphql_type=str, description="""Should be `ok` if descired state has been reached, otherwise `fail`.
For update operation fail should be also stated when bad lastchange has been entered.""")


def createRootResolver_by_id(scalarType: None, description="Retrieves item by its id"):
    assert scalarType is not None

    @strawberry.field(description=description)
    async def by_id(
            self, info: strawberry.types.Info, id: uuid.UUID
    ) -> typing.Optional[scalarType]:
        result = await scalarType.resolve_reference(info=info, id=id)
        return result

    return by_id


# def createRootResolver_by_page(
#         scalarType: None,
#         whereFilterType: None,
#         loaderLambda=lambda info: None,
#         description="Retrieves items paged",
#         skip: int = 0,
#         limit: int = 10,
#         order_by: typing.Optional[str] = None,
#         desc: typing.Optional[bool] = None):
#         assert scalarType is not None
#         assert whereFilterType is not None

    # @strawberry.field(description=description)
    # async def paged(
    #         self, info: strawberry.types.Info,
    #         skip: int = skip, limit: int = limit, where: typing.Optional[whereFilterType] = None
    # ) -> typing.List[scalarType]:
    #     loader = loaderLambda(info)
    #     assert loader is not None
    #     wf = None if where is None else strawberry.asdict(where)
    #     result = await loader.page(skip=skip, limit=limit, where=wf)
    #     return result

    # return paged