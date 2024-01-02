import graphene

from accounts.schemas import AccountMutation, AccountQuery
from authentication.schemas import AuthMutation
from currencies.schemas import CurrencyMutation, CurrencyQuery
from thriftease_api import settings
from users.schemas import UserMutation, UserQuery


class Query(UserQuery, CurrencyQuery, AccountQuery, graphene.ObjectType):
    if settings.DEBUG:
        test = graphene.String(default_value="Queried!")


class Mutation(
    UserMutation, AuthMutation, CurrencyMutation, AccountMutation, graphene.ObjectType
):
    if settings.DEBUG:
        test = graphene.String(default_value="Mutated!")


schema = graphene.Schema(query=Query, mutation=Mutation)
