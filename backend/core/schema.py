import strawberry
from users.schema import Query as UsersQuery, Mutation as UsersMutation
from properties.schema import Query as PropertiesQuery, Mutation as PropertiesMutation

@strawberry.type
class Query(UsersQuery, PropertiesQuery):
    @strawberry.field
    def hello(self) -> str:
        return "The API is running."

@strawberry.type
class Mutation(UsersMutation, PropertiesMutation):
    pass

schema = strawberry.Schema(query=Query, mutation=Mutation)