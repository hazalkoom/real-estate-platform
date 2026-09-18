import strawberry
from users.schema import Query as UsersQuery, Mutation as UsersMutation
from properties.schema import Query as PropertiesQuery, Mutation as PropertiesMutation
from interactions.schema import Query as InteractionsQuery, Mutation as InteractionsMutation
from strawberry_django.optimizer import DjangoOptimizerExtension

@strawberry.type
class Query(UsersQuery, PropertiesQuery, InteractionsQuery):
    @strawberry.field
    def hello(self) -> str:
        return "The API is running."

@strawberry.type
class Mutation(UsersMutation, PropertiesMutation, InteractionsMutation):
    pass

schema = strawberry.Schema(
    query=Query,
    mutation=Mutation,
    extensions=[
        DjangoOptimizerExtension,
    ]
)