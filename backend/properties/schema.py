import strawberry
import strawberry_django
from .types import PropertyNode, ListingNode, AmenityNode, PropertyTypeNode

@strawberry.type
class Query:
    properties: list[PropertyNode] = strawberry_django.field()
    listings: list[ListingNode] = strawberry_django.field()
    amenities: list[AmenityNode] = strawberry_django.field()
    property_types: list[PropertyTypeNode] = strawberry_django.field()