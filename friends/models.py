from datetime import date

from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models
from django.urls import reverse


class ConnectionGroup(models.Model):
    CATEGORY_CHOICES = [
        ("school", "School"),
        ("college", "College / Sixth Form"),
        ("university", "University"),
        ("work", "Work"),
        ("online", "Online"),
        ("family", "Family"),
        ("other", "Other"),
    ]

    name = models.CharField(max_length=120, unique=True)
    category = models.CharField(max_length=30, choices=CATEGORY_CHOICES, default="other")
    description = models.TextField(blank=True)
    colour_hex = models.CharField(max_length=7, default="#F3A0A8")
    display_order = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ["display_order", "name"]

    def __str__(self):
        return self.name


class Friend(models.Model):
    TIER_CHOICES = [
        ("inner_circle", "Inner Circle"),
        ("friend", "Friend"),
        ("archive", "Archive"),
    ]

    MBTI_CHOICES = [
        ("", "Unknown / Not added"),
        ("INTJ", "INTJ"),
        ("INTP", "INTP"),
        ("ENTJ", "ENTJ"),
        ("ENTP", "ENTP"),
        ("INFJ", "INFJ"),
        ("INFP", "INFP"),
        ("ENFJ", "ENFJ"),
        ("ENFP", "ENFP"),
        ("ISTJ", "ISTJ"),
        ("ISFJ", "ISFJ"),
        ("ESTJ", "ESTJ"),
        ("ESFJ", "ESFJ"),
        ("ISTP", "ISTP"),
        ("ISFP", "ISFP"),
        ("ESTP", "ESTP"),
        ("ESFP", "ESFP"),
    ]

    ZODIAC_CHOICES = [
        ("", "Unknown / Not added"),
        ("Aries", "Aries"),
        ("Taurus", "Taurus"),
        ("Gemini", "Gemini"),
        ("Cancer", "Cancer"),
        ("Leo", "Leo"),
        ("Virgo", "Virgo"),
        ("Libra", "Libra"),
        ("Scorpio", "Scorpio"),
        ("Sagittarius", "Sagittarius"),
        ("Capricorn", "Capricorn"),
        ("Aquarius", "Aquarius"),
        ("Pisces", "Pisces"),
    ]

    MORNING_NIGHT_CHOICES = [
        ("", "Unknown / Not added"),
        ("morning", "Morning person"),
        ("night", "Night person"),
        ("both", "Both"),
        ("neither", "Neither"),
    ]

    SOURCE_CHOICES = [
        ("manual", "Manual entry"),
        ("google_form", "Google Form"),
        ("spreadsheet", "Spreadsheet"),
        ("other", "Other"),
    ]

    first_name = models.CharField(max_length=80)
    last_name = models.CharField(max_length=80, blank=True)
    nickname = models.CharField(max_length=80, blank=True)

    profile_picture = models.ImageField(
        upload_to="friend_profiles/",
        blank=True,
        null=True,
    )

    birthday = models.DateField(blank=True, null=True)
    how_we_met = models.TextField(blank=True)

    connection_group = models.ForeignKey(
        ConnectionGroup,
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        related_name="friends",
    )

    tier = models.CharField(max_length=30, choices=TIER_CHOICES, default="friend")

    favourite_colour = models.CharField(max_length=80, blank=True)
    favourite_food = models.CharField(max_length=120, blank=True)
    favourite_restaurant = models.CharField(max_length=120, blank=True)
    favourite_alcoholic_drink = models.CharField(max_length=120, blank=True)
    favourite_season = models.CharField(max_length=80, blank=True)

    morning_or_night = models.CharField(
        max_length=20,
        choices=MORNING_NIGHT_CHOICES,
        blank=True,
    )

    mbti = models.CharField(max_length=10, choices=MBTI_CHOICES, blank=True)
    zodiac = models.CharField(max_length=20, choices=ZODIAC_CHOICES, blank=True)

    hobbies = models.TextField(blank=True)
    sports_team = models.CharField(max_length=120, blank=True)
    notes = models.TextField(blank=True)

    data_source = models.CharField(max_length=30, choices=SOURCE_CHOICES, default="manual")

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["first_name", "last_name"]

    def __str__(self):
        return self.full_name

    @property
    def full_name(self):
        name = f"{self.first_name} {self.last_name}".strip()
        return name

    @property
    def display_name(self):
        if self.nickname:
            return f"{self.full_name} ({self.nickname})"
        return self.full_name

    @property
    def age(self):
        if not self.birthday:
            return None

        today = date.today()
        age = today.year - self.birthday.year

        if (today.month, today.day) < (self.birthday.month, self.birthday.day):
            age -= 1

        return age

    @property
    def next_birthday_date(self):
        if not self.birthday:
            return None

        today = date.today()

        try:
            next_birthday = date(today.year, self.birthday.month, self.birthday.day)
        except ValueError:
            next_birthday = date(today.year, 3, 1)

        if next_birthday < today:
            try:
                next_birthday = date(today.year + 1, self.birthday.month, self.birthday.day)
            except ValueError:
                next_birthday = date(today.year + 1, 3, 1)

        return next_birthday

    @property
    def days_until_birthday(self):
        next_birthday = self.next_birthday_date

        if not next_birthday:
            return None

        return (next_birthday - date.today()).days

    def get_absolute_url(self):
        return reverse("friends:friend_profile", args=[self.pk])


class ExtendedProfile(models.Model):
    friend = models.OneToOneField(
        Friend,
        on_delete=models.CASCADE,
        related_name="extended_profile",
    )

    favourite_song = models.CharField(max_length=150, blank=True)
    favourite_movie = models.CharField(max_length=150, blank=True)
    favourite_show = models.CharField(max_length=150, blank=True)
    dream_trip = models.CharField(max_length=150, blank=True)
    gift_ideas = models.TextField(blank=True)
    inside_jokes = models.TextField(blank=True)
    friendship_story = models.TextField(blank=True)
    favourite_memory = models.TextField(blank=True)
    private_notes = models.TextField(blank=True)

    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Extended profile for {self.friend.full_name}"


class Memory(models.Model):
    title = models.CharField(max_length=160)
    friends = models.ManyToManyField(Friend, related_name="memories", blank=True)

    description = models.TextField()
    date = models.DateField(blank=True, null=True)

    location_name = models.CharField(max_length=160, blank=True)
    latitude = models.DecimalField(
        max_digits=9,
        decimal_places=6,
        blank=True,
        null=True,
        validators=[MinValueValidator(-90), MaxValueValidator(90)],
    )
    longitude = models.DecimalField(
        max_digits=9,
        decimal_places=6,
        blank=True,
        null=True,
        validators=[MinValueValidator(-180), MaxValueValidator(180)],
    )

    mood = models.CharField(max_length=80, blank=True)
    tags = models.CharField(
        max_length=255,
        blank=True,
        help_text="Comma-separated tags, for example: cinema, school, funny",
    )

    is_favourite = models.BooleanField(default=False)

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-date", "-created_at"]

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        return reverse("friends:memory_detail", args=[self.pk])


class Photo(models.Model):
    friend = models.ForeignKey(
        Friend,
        on_delete=models.CASCADE,
        related_name="photos",
        blank=True,
        null=True,
    )

    memory = models.ForeignKey(
        Memory,
        on_delete=models.CASCADE,
        related_name="photos",
        blank=True,
        null=True,
    )

    image = models.ImageField(upload_to="gallery/")
    caption = models.CharField(max_length=180, blank=True)
    taken_on = models.DateField(blank=True, null=True)

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-taken_on", "-created_at"]

    def __str__(self):
        if self.caption:
            return self.caption

        if self.friend:
            return f"Photo of {self.friend.full_name}"

        if self.memory:
            return f"Photo for {self.memory.title}"

        return "Photo"