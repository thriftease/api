import graphene

from accounts.schemas import AccountMutation, AccountQuery
from authentication.schemas import AuthMutation, AuthQuery
from currencies.schemas import CurrencyMutation, CurrencyQuery
from tags.schemas import TagMutation, TagQuery
from thriftease_api import settings
from transactions.schemas import TransactionMutation, TransactionQuery
from users.schemas import UserMutation, UserQuery


class Query(
    UserQuery,
    AuthQuery,
    CurrencyQuery,
    AccountQuery,
    TransactionQuery,
    TagQuery,
    graphene.ObjectType,
):
    if settings.DEBUG:
        test = graphene.String(default_value="Queried!")


class Mutation(
    UserMutation,
    AuthMutation,
    CurrencyMutation,
    AccountMutation,
    TransactionMutation,
    TagMutation,
    graphene.ObjectType,
):
    if settings.DEBUG:
        test = graphene.String(default_value="Mutated!")


schema = graphene.Schema(query=Query, mutation=Mutation)
