import strawberry
from users.schema import Query as UsersQuery
from properties.schema import Query as PropertiesQuery, Mutation as PropertiesMutation

@strawberry.type
class Query(UsersQuery, PropertiesQuery):
    @strawberry.field
    def hello(self) -> str:
        return "The api is running"

@strawberry.type
class Mutation(PropertiesMutation):
    pass

schema = strawberry.Schema(query=Query, mutation=Mutation)