from django.db import models


SOURCE_CHOICES = (
    ('youtube', 'YouTube'),
    ('twitter', 'Twitter'),
)

VALIDATION_CHOICES = (
    ('verified', 'Verified'),
    ('questionable', 'Questionable'),
    ('debunked', 'Debunked'),
)

# TODO
CLAIM_CATEGORIES = (

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
    podcast_playlist = models.CharField(max_length=255)


# TODO source link, score int or float?
class Claim(BaseModel):
    influencer = models.ForeignKey(Influencer, on_delete=models.CASCADE)
    source_type = models.CharField(max_length=255, choices=SOURCE_CHOICES)
    source_id = models.CharField(max_length=255)
    score = models.FloatField()
    claim = models.TextField()
    validation = models.CharField(max_length=255, choices=VALIDATION_CHOICES)
    category = models.CharField(max_length=255, choices=CLAIM_CATEGORIES)
