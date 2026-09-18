import factory
from django.utils import timezone
from interactions.models import Favorite, TourRequest, Review

# Assuming you have these factories in your other apps. 
# If your import paths are different, fix them yourself, ya ghabi.
from users.tests.factories import UserFactory
from properties.tests.factories import ListingFactory

class FavoriteFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Favorite

    user = factory.SubFactory(UserFactory)
    listing = factory.SubFactory(ListingFactory)

class TourRequestFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = TourRequest

    buyer = factory.SubFactory(UserFactory)
    listing = factory.SubFactory(ListingFactory)
    tour_date = factory.Faker('future_datetime', tzinfo=timezone.utc)
    status = TourRequest.TourStatus.PENDING
    message = factory.Faker('sentence')

class ReviewFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Review

    reviewer = factory.SubFactory(UserFactory)
    agent = factory.SubFactory(UserFactory, is_agent=True)
    rating = factory.Faker('random_int', min=1, max=5)
    comment = factory.Faker('text')