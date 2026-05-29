from django.contrib import admin

from .models import ConnectionGroup, ExtendedProfile, Friend, Memory, Photo


class ExtendedProfileInline(admin.StackedInline):
    model = ExtendedProfile
    extra = 0


class PhotoInline(admin.TabularInline):
    model = Photo
    extra = 0


@admin.register(ConnectionGroup)
class ConnectionGroupAdmin(admin.ModelAdmin):
    list_display = ("name", "category", "colour_hex", "display_order")
    list_filter = ("category",)
    search_fields = ("name", "description")
    ordering = ("display_order", "name")


@admin.register(Friend)
class FriendAdmin(admin.ModelAdmin):
    list_display = (
        "display_name_admin",
        "tier",
        "connection_group",
        "birthday",
        "age_admin",
        "zodiac",
        "mbti",
        "created_at",
    )

    list_filter = (
        "tier",
        "connection_group",
        "zodiac",
        "mbti",
        "favourite_season",
        "morning_or_night",
        "data_source",
    )

    search_fields = (
        "first_name",
        "last_name",
        "nickname",
        "how_we_met",
        "favourite_colour",
        "favourite_food",
        "hobbies",
        "notes",
    )

    readonly_fields = ("created_at", "updated_at", "age_admin", "days_until_birthday_admin")

    fieldsets = (
        (
            "Basic Friend Details",
            {
                "fields": (
                    "first_name",
                    "last_name",
                    "nickname",
                    "profile_picture",
                    "tier",
                    "data_source",
                )
            },
        ),
        (
            "Birthday and How You Met",
            {
                "fields": (
                    "birthday",
                    "age_admin",
                    "days_until_birthday_admin",
                    "how_we_met",
                    "connection_group",
                )
            },
        ),
        (
            "Personality and Favourite Things",
            {
                "fields": (
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
                )
            },
        ),
        (
            "Notes",
            {
                "fields": (
                    "notes",
                )
            },
        ),
        (
            "System Dates",
            {
                "fields": (
                    "created_at",
                    "updated_at",
                )
            },
        ),
    )

    inlines = [ExtendedProfileInline, PhotoInline]

    @admin.display(description="Friend")
    def display_name_admin(self, obj):
        return obj.display_name

    @admin.display(description="Age")
    def age_admin(self, obj):
        return obj.age if obj.age is not None else "Not added"

    @admin.display(description="Days until birthday")
    def days_until_birthday_admin(self, obj):
        if obj.days_until_birthday is None:
            return "Not added"

        if obj.days_until_birthday == 0:
            return "Today"

        return obj.days_until_birthday


@admin.register(ExtendedProfile)
class ExtendedProfileAdmin(admin.ModelAdmin):
    list_display = ("friend", "favourite_song", "favourite_movie", "updated_at")
    search_fields = (
        "friend__first_name",
        "friend__last_name",
        "favourite_song",
        "favourite_movie",
        "favourite_show",
        "friendship_story",
        "private_notes",
    )


@admin.register(Memory)
class MemoryAdmin(admin.ModelAdmin):
    list_display = ("title", "date", "location_name", "is_favourite", "created_at")
    list_filter = ("is_favourite", "date", "location_name")
    search_fields = ("title", "description", "location_name", "tags")
    filter_horizontal = ("friends",)
    readonly_fields = ("created_at",)

    fieldsets = (
        (
            "Memory Details",
            {
                "fields": (
                    "title",
                    "friends",
                    "description",
                    "date",
                    "is_favourite",
                )
            },
        ),
        (
            "Memory Map Location",
            {
                "fields": (
                    "location_name",
                    "latitude",
                    "longitude",
                )
            },
        ),
        (
            "Extra Details",
            {
                "fields": (
                    "mood",
                    "tags",
                    "created_at",
                )
            },
        ),
    )


@admin.register(Photo)
class PhotoAdmin(admin.ModelAdmin):
    list_display = ("caption", "friend", "memory", "taken_on", "created_at")
    list_filter = ("taken_on", "created_at")
    search_fields = (
        "caption",
        "friend__first_name",
        "friend__last_name",
        "memory__title",
    )