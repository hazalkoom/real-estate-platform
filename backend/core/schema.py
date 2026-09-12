import strawberry
from users.schema import Query as UsersQuery

@strawberry.type
class Query(UsersQuery):
    @strawberry.field
    def hello(self) -> str:
        return "The api is running"

schema = strawberry.Schema(query=Query)