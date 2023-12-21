from utils.gql import GqlAction, GqlMutation, GqlQuery, GqlType


class Schema:
    ErrorType = GqlType("field", "messages")

    @classmethod
    def mutation(cls, *actions: GqlAction):
        return GqlMutation(*actions)

    @classmethod
    def query(cls, *actions: GqlAction):
        return GqlQuery(*actions)
