import strawberry
from users.schema import Query as UsersQuery
from properties.schema import Query as PropertiesQuery

@strawberry.type
class Query(UsersQuery, PropertiesQuery):
    @strawberry.field
    def hello(self) -> str:
        return "The api is running"

schema = strawberry.Schema(query=Query)