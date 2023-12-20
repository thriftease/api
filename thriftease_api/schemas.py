import graphene

from authentication.schemas import AuthMutation
from thriftease_api import settings
from users.schemas import UserMutation, UserQuery


class Query(UserQuery, graphene.ObjectType):
    if settings.DEBUG:
        test = graphene.String(default_value="Queried!")


class Mutation(UserMutation, AuthMutation, graphene.ObjectType):
    if settings.DEBUG:
        test = graphene.String(default_value="Mutated!")


schema = graphene.Schema(query=Query, mutation=Mutation)
