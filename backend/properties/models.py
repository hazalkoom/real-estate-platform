from django.db import models
from django.conf import settings
from core.models import TimeStampedModel, SoftDeleteModel
# Create your models here.

class PropertyType(TimeStampedModel):
    name = models.CharField(max_length=100, unique=True)
    
    def __str__(self):
        return self.name

class Amenity(TimeStampedModel):
    name = models.CharField(max_length=100, unique=True)
    
    def __str__(self):
        return self.name

class Location(TimeStampedModel):
    city = models.CharField(max_length=100, db_index=True)
    district = models.CharField(max_length=100, db_index=True)
    address = models.TextField()
    latitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    longitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)

    def __str__(self):
        return f"{self.address}, {self.city}"


class Property(TimeStampedModel, SoftDeleteModel):
    owner = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='owned_properties')
    property_type = models.ForeignKey(PropertyType, on_delete=models.PROTECT, related_name='properties')
    location = models.OneToOneField(Location, on_delete=models.CASCADE, related_name='property')
    bedrooms = models.PositiveIntegerField(default=0)
    bathrooms = models.PositiveIntegerField(default=0)
    area = models.DecimalField(max_digits=10, decimal_places=2, help_text="Area in square meters")
    amenities = models.ManyToManyField(Amenity, related_name='properties', blank=True)
    description = models.TextField(blank=True)

    def __str__(self):
        return f"{self.property_type.name} at {self.location.city}"

class PropertyMedia(TimeStampedModel):
    property = models.ForeignKey(Property, on_delete=models.CASCADE, related_name='media')
    url = models.URLField(max_length=500)
    media_type = models.CharField(max_length=50, default='image')
    is_primary = models.BooleanField(default=False)

    def __str__(self):
        return f"Media for {self.property.id}"


class Listing(TimeStampedModel, SoftDeleteModel):
    class ListingType(models.TextChoices):
        SALE = 'SALE', 'Sale'
        RENT = 'RENT', 'Rent'

    class ListingStatus(models.TextChoices):
        ACTIVE = 'ACTIVE', 'Active'
        PENDING = 'PENDING', 'Pending'
        SOLD = 'SOLD', 'Sold'
        RENTED = 'RENTED', 'Rented'
        EXPIRED = 'EXPIRED', 'Expired'

    property = models.OneToOneField(Property, on_delete=models.CASCADE, related_name='listing')
    agent = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True, related_name='managed_listings')
    listing_type = models.CharField(max_length=10, choices=ListingType.choices)
    status = models.CharField(max_length=20, choices=ListingStatus.choices, default=ListingStatus.ACTIVE)
    price = models.DecimalField(max_digits=12, decimal_places=2, db_index=True)

    def __str__(self):
        return f"{self.listing_type} - {self.property} - {self.status}"