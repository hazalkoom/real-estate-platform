import strawberry

@strawberry.type
class Query:
    @strawberry.field
    def hello(self) -> str:
        return "The api is running"

schema = strawberry.Schema(query=Query)