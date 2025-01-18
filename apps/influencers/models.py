from django.db import models


SOURCE_CHOICES = (
    ("youtube", "YouTube"),
    ("twitter", "Twitter"),
)

VALIDATION_CHOICES = (
    ("verified", "Verified"),
    ("questionable", "Questionable"),
    ("debunked", "Debunked"),
)

CLAIM_CATEGORIES = (
    ("nutrition", "Nutrition"),
    ("exercise", "Exercise"),
    ("mental_health", "Mental Health"),
    ("sleep", "Sleep"),
    ("chronic_illness_management", "Chronic Illness Management"),
    ("supplements", "Supplements"),
    ("other", "Other"),
)


class BaseModel(models.Model):
    updated = models.DateTimeField(auto_now=True)
    created = models.DateTimeField(auto_now_add=True)
    deleted = models.BooleanField(default=False)

    class Meta:
        abstract = True


# TODO slugs for names? define defaults
class Influencer(BaseModel):
    # youtube id as a primary key
    youtube_id = models.CharField(max_length=255)
    twitter_id = models.CharField(max_length=255, null=True, blank=True)
    youtube_pp = models.CharField(max_length=255)
    name = models.CharField(max_length=255)
    description = models.TextField()
    followers = models.IntegerField()
    earnings = models.CharField(max_length=255, null=True, blank=True)
    podcast_playlist = models.CharField(max_length=255, null=True, blank=True)


# TODO source link, score int or float?
class Claim(BaseModel):
    influencer = models.ForeignKey(Influencer, on_delete=models.CASCADE)
    source_type = models.CharField(max_length=255, choices=SOURCE_CHOICES)
    source_id = models.CharField(max_length=255)
    validation_sources = models.JSONField(default=list)
    score = models.FloatField()
    claim = models.TextField()
    validation = models.CharField(max_length=255, choices=VALIDATION_CHOICES)
    category = models.CharField(max_length=255, choices=CLAIM_CATEGORIES)
