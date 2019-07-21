from django.db import models, transaction
from django.contrib.auth.models import User
from django.urls import reverse
from html5tagger import E
from django.contrib.staticfiles.storage import staticfiles_storage
from .slugs import USlugField, LSlugField
import re
import uuid

def static(filename):
    """Return URL for this app's static file."""
    return staticfiles_storage.url("webshop/" + filename)

HISCORE_LEN = 5   # Number of entries per game

class Developer(models.Model):
    """Game developer / user type"""
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    slug = USlugField(unique=True, help_text="Developer name in webshop URLs")
    name = models.CharField(max_length=50, unique=True)
    description = models.TextField(blank=True)
    registered = models.DateField(auto_now=True)
    def __str__(self): return self.slug
    def get_absolute_url(self):
        return reverse("webshop:developer", kwargs=dict(devslug=self.slug))
    def get_link(self):
        return E.a(self.name, href=self.get_absolute_url(), title=self.description)
    def has_access(self, user):
        """Return True if user has access (is this developer or is admin)."""
        return hasattr(user, "developer") and user.developer == self or user.has_perm("webshop.admin")
    class Meta:
        ordering = "name",
        permissions = ("admin", "Full access to all games"),

class Genre(models.Model):
    """Game genre"""
    slug = LSlugField(unique=True, help_text="Genre name in webshop URLs")
    name = models.CharField(max_length=30, unique=True)
    description = models.TextField(blank=True)
    def __str__(self): return self.name
    def get_absolute_url(self):
        return reverse("webshop:genre", kwargs=dict(genreslug=self.slug))
    class Meta:
        ordering = "name",

class Game(models.Model):
    """Game object"""
    # Note: slug and developer unique together would be enough, but form validation
    # doesn't understand it, so we require unique slugs not just per developer.
    slug = USlugField(unique=True, help_text="Game name in webshop URLs")
    name = models.CharField(max_length=50)
    description = models.TextField(blank=True)
    def image_path(self, filename):
        ext = re.search(".(png|svg|webp)$", filename.lower())
        ext = ext[1] if ext else "jpg"  # Fallback to jpegs...
        return f"games/img-{self.pk}.{ext}"
    image = models.ImageField(blank=True, upload_to=image_path, help_text="Square-shaped image/icon for the game.")
    developer = models.ForeignKey(Developer, on_delete=models.CASCADE, related_name="games")
    url = models.URLField(help_text="Address where the game may be played, used in iframe.")
    price = models.DecimalField(max_digits=5, decimal_places=2, default="0.00")
    users = models.ManyToManyField(User, related_name="games", blank=True, help_text="Who have purchased this game")
    genres = models.ManyToManyField(Genre, related_name="games", help_text="One to three genres may be chosen")
    popularity = models.FloatField(default=0)
    published = models.DateField(auto_now=True)
    def __str__(self): return self.slug
    def get_absolute_url(self):
        return reverse("webshop:game", kwargs=dict(devslug=self.developer.slug, gameslug=self.slug))
    def has_access(self, user):
        """Return True if user is allowed to access/play this game."""
        if not self.price: return True
        if not user.is_authenticated: return False
        return user.games.filter(pk=self.pk) or self.developer.has_access(user)
    def purchase(self, user, price, ref):
        Sale(developer=self.developer, buyer=user, game=self, price=price, ref=ref).save()
        self.users.add(user)
    def update_popularity(self, increase=1.0):
        """Whenever game is accessed, its popularity is increased."""
        self.popularity += increase
        self.save()
    def get_image(self):
        if not self.image: return static("game.svg")
        return self.image.url
    def get_hiscores_list(self, padding=True):
        """Returns a list of tuples with name and score to be displayed in UI"""
        ret = [(s.user.username, f"{s.score:.0f}") for s in self.hiscores.all()]
        if padding: ret += (HISCORE_LEN - len(ret)) * [("…", "0")]
        return ret
    class Meta:
        ordering = "-popularity",
        unique_together = ("slug", "developer"),

class Hiscore(models.Model):
    """Record of top scores"""
    game = models.ForeignKey(Game, models.CASCADE, related_name="hiscores")
    user = models.ForeignKey(User, models.CASCADE, related_name="hiscores")
    score = models.FloatField()
    date = models.DateField(auto_now=True)
    def __str__(self): return f"{self.game.slug} {self.user} {self.score}"
    class Meta:
        ordering = "-score",

def submit_hiscore(game, user, score):
    if not score > 0.0: return None  # Negative or NaN not accepted
    with transaction.atomic():
        hiscores = [hs for hs in Hiscore.objects.filter(game=game)]
        print(len(hiscores))
        if len(hiscores) >= HISCORE_LEN and hiscores[-1].score >= score: return None  # Not high enough
        for hs in hiscores[HISCORE_LEN - 1:]: hs.delete() # Limit to 5 entries
        hs = Hiscore(game=game, user=user, score=score)
        hs.save()
    return hs

class Savegame(models.Model):
    """A saved session with game state JSON"""
    game = models.ForeignKey(Game, models.CASCADE, related_name="savegames")
    user = models.ForeignKey(User, models.CASCADE, related_name="savegames")
    state = models.TextField()
    date = models.DateField(auto_now=True)
    class Meta:
        #ordering = "game", "user",
        unique_together = ("game", "user"),

class Sale(models.Model):
    """Sales log"""
    developer = models.ForeignKey(Developer, models.CASCADE, related_name="sales")
    buyer = models.ForeignKey(User, models.SET_NULL, blank=True, null=True, related_name="sales")
    game = models.ForeignKey(Game, models.SET_NULL, blank=True, null=True, related_name="sales")
    price = models.DecimalField(max_digits=5, decimal_places=2)
    ref = models.CharField(max_length=50, unique=True)
    date = models.DateTimeField(auto_now=True)
    class Meta:
        ordering = "-date",

class Payment(models.Model):
    """Payments currently in progress"""
    pid = models.UUIDField(primary_key=True, default=uuid.uuid4)
    user = models.ForeignKey(User, models.CASCADE)
    game = models.ForeignKey(Game, models.SET_NULL, null=True)
    price = models.DecimalField(max_digits=5, decimal_places=2)
    date = models.DateTimeField(auto_now=True)
