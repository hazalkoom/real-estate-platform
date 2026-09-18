from django.db import models
from django.conf import settings
from core.models import TimeStampedModel
from properties.models import Listing

class Favorite(TimeStampedModel):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='favorites')
    listing = models.ForeignKey(Listing, on_delete=models.CASCADE, related_name='favorited_by')

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['user', 'listing'], name='unique_user_favorite_listing')
        ]
        
    def __str__(self):
        return f"{self.user.email} - {self.listing.id}"

class TourRequest(TimeStampedModel):
    class TourStatus(models.TextChoices):
        PENDING = 'PENDING', 'Pending'
        ACCEPTED = 'ACCEPTED', 'Accepted'
        REJECTED = 'REJECTED', 'Rejected'
        COMPLETED = 'COMPLETED', 'Completed'
        CANCELLED = 'CANCELLED', 'Cancelled'

    buyer = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='tours_requested')
    listing = models.ForeignKey(Listing, on_delete=models.CASCADE, related_name='tour_requests')
    tour_date = models.DateTimeField()
    status = models.CharField(max_length=20, choices=TourStatus.choices, default=TourStatus.PENDING)
    message = models.TextField(blank=True)

    def __str__(self):
        return f"Tour {self.id} for {self.listing.id} by {self.buyer.email}"

class Review(TimeStampedModel):
    reviewer = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='reviews_given')
    agent = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='reviews_received')
    rating = models.IntegerField(choices=[(i, i) for i in range(1, 6)])
    comment = models.TextField(blank=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['reviewer', 'agent'], name='unique_agent_review_by_user')
        ]

    def __str__(self):
        return f"Review by {self.reviewer.email} for {self.agent.email} - {self.rating} Stars"