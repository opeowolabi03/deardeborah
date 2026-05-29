from django import forms

from .models import ExtendedProfile, Friend, Memory, Photo


class FriendForm(forms.ModelForm):
    class Meta:
        model = Friend
        fields = [
            "first_name",
            "last_name",
            "nickname",
            "profile_picture",
            "birthday",
            "how_we_met",
            "connection_group",
            "tier",
            "favourite_colour",
            "favourite_food",
            "favourite_restaurant",
            "favourite_alcoholic_drink",
            "favourite_season",
            "morning_or_night",
            "mbti",
            "zodiac",
            "hobbies",
            "sports_team",
            "notes",
            "data_source",
        ]

        widgets = {
            "birthday": forms.DateInput(attrs={"type": "date"}),
            "how_we_met": forms.Textarea(attrs={"rows": 4}),
            "hobbies": forms.Textarea(attrs={"rows": 3}),
            "notes": forms.Textarea(attrs={"rows": 4}),
        }


class ExtendedProfileForm(forms.ModelForm):
    class Meta:
        model = ExtendedProfile
        fields = [
            "favourite_song",
            "favourite_movie",
            "favourite_show",
            "dream_trip",
            "gift_ideas",
            "inside_jokes",
            "friendship_story",
            "favourite_memory",
            "private_notes",
        ]

        widgets = {
            "gift_ideas": forms.Textarea(attrs={"rows": 3}),
            "inside_jokes": forms.Textarea(attrs={"rows": 3}),
            "friendship_story": forms.Textarea(attrs={"rows": 4}),
            "favourite_memory": forms.Textarea(attrs={"rows": 4}),
            "private_notes": forms.Textarea(attrs={"rows": 4}),
        }


class MemoryForm(forms.ModelForm):
    class Meta:
        model = Memory
        fields = [
            "title",
            "friends",
            "description",
            "date",
            "location_name",
            "latitude",
            "longitude",
            "mood",
            "tags",
            "is_favourite",
        ]

        widgets = {
            "date": forms.DateInput(attrs={"type": "date"}),
            "description": forms.Textarea(attrs={"rows": 5}),
            "friends": forms.CheckboxSelectMultiple,
        }


class PhotoForm(forms.ModelForm):
    class Meta:
        model = Photo
        fields = [
            "friend",
            "memory",
            "image",
            "caption",
            "taken_on",
        ]

        widgets = {
            "taken_on": forms.DateInput(attrs={"type": "date"}),
        }


class SearchForm(forms.Form):
    query = forms.CharField(
        label="Search",
        required=False,
        max_length=120,
        help_text="Search by name, food, hobby, school, colour, memory, MBTI, zodiac, or notes.",
    )