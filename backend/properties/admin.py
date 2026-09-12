from django.contrib import admin
from .models import PropertyType, Amenity, Location, Property, PropertyMedia, Listing

admin.site.register(PropertyType)
admin.site.register(Amenity)
admin.site.register(Location)
admin.site.register(PropertyMedia)

@admin.register(Property)
class PropertyAdmin(admin.ModelAdmin):
    list_display = ('id', 'property_type', 'location', 'owner', 'is_deleted')
    list_filter = ('property_type', 'is_deleted')
    search_fields = ('location__city', 'location__address')

@admin.register(Listing)
class ListingAdmin(admin.ModelAdmin):
    list_display = ('id', 'property', 'listing_type', 'status', 'price', 'agent', 'is_deleted')
    list_filter = ('listing_type', 'status', 'is_deleted')
    search_fields = ('property__location__city',)