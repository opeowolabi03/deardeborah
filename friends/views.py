from collections import defaultdict

from django.db.models import Count, Q
from django.shortcuts import get_object_or_404, redirect, render

from .forms import FriendForm, SearchForm
from .models import ConnectionGroup, Friend, Memory, Photo


def home(request):
    friend_count = Friend.objects.count()
    memory_count = Memory.objects.count()
    photo_count = Photo.objects.count()
    inner_circle_count = Friend.objects.filter(tier="inner_circle").count()

    recent_friends = Friend.objects.order_by("-created_at")[:5]

    friends_with_birthdays = list(Friend.objects.exclude(birthday__isnull=True))
    upcoming_birthdays = sorted(
        friends_with_birthdays,
        key=lambda friend: friend.days_until_birthday,
    )[:5]

    favourite_memories = Memory.objects.filter(is_favourite=True)[:4]

    context = {
        "friend_count": friend_count,
        "memory_count": memory_count,
        "photo_count": photo_count,
        "inner_circle_count": inner_circle_count,
        "recent_friends": recent_friends,
        "upcoming_birthdays": upcoming_birthdays,
        "favourite_memories": favourite_memories,
    }

    return render(request, "friends/home.html", context)


def friend_directory(request):
    query = request.GET.get("q", "").strip()
    tier = request.GET.get("tier", "").strip()
    connection_group_id = request.GET.get("connection_group", "").strip()

    friends = Friend.objects.select_related("connection_group").all()

    if query:
        friends = friends.filter(
            Q(first_name__icontains=query)
            | Q(last_name__icontains=query)
            | Q(nickname__icontains=query)
            | Q(how_we_met__icontains=query)
            | Q(favourite_colour__icontains=query)
            | Q(favourite_food__icontains=query)
            | Q(hobbies__icontains=query)
            | Q(notes__icontains=query)
            | Q(connection_group__name__icontains=query)
        )

    if tier:
        friends = friends.filter(tier=tier)

    if connection_group_id:
        friends = friends.filter(connection_group_id=connection_group_id)

    connection_groups = ConnectionGroup.objects.all()

    context = {
        "friends": friends,
        "query": query,
        "selected_tier": tier,
        "selected_connection_group": connection_group_id,
        "connection_groups": connection_groups,
        "tier_choices": Friend.TIER_CHOICES,
    }

    return render(request, "friends/friend_directory.html", context)


def add_friend(request):
    if request.method == "POST":
        form = FriendForm(request.POST, request.FILES)

        if form.is_valid():
            friend = form.save()
            return redirect(friend.get_absolute_url())
    else:
        form = FriendForm()

    context = {
        "form": form,
    }

    return render(request, "friends/add_friend.html", context)


def friend_profile(request, pk):
    friend = get_object_or_404(
        Friend.objects.select_related("connection_group"),
        pk=pk,
    )

    memories = friend.memories.all()[:10]
    photos = friend.photos.all()[:10]
    extended_profile = getattr(friend, "extended_profile", None)

    context = {
        "friend": friend,
        "memories": memories,
        "photos": photos,
        "extended_profile": extended_profile,
    }

    return render(request, "friends/friend_profile.html", context)


def memories(request):
    all_memories = Memory.objects.prefetch_related("friends").all()

    context = {
        "memories": all_memories,
    }

    return render(request, "friends/memories.html", context)


def memory_detail(request, pk):
    memory = get_object_or_404(
        Memory.objects.prefetch_related("friends", "photos"),
        pk=pk,
    )

    context = {
        "memory": memory,
    }

    return render(request, "friends/memory_detail.html", context)


def memory_map(request):
    memories_with_locations = (
        Memory.objects.exclude(location_name="")
        .prefetch_related("friends")
        .order_by("-date", "-created_at")
    )

    context = {
        "memories": memories_with_locations,
    }

    return render(request, "friends/memory_map.html", context)


def birthday_calendar(request):
    month_groups = defaultdict(list)

    friends = Friend.objects.exclude(birthday__isnull=True)

    for friend in friends:
        month_groups[friend.birthday.month].append(friend)

    month_names = {
        1: "January",
        2: "February",
        3: "March",
        4: "April",
        5: "May",
        6: "June",
        7: "July",
        8: "August",
        9: "September",
        10: "October",
        11: "November",
        12: "December",
    }

    months = []

    for month_number in range(1, 13):
        friends_in_month = sorted(
            month_groups[month_number],
            key=lambda friend: friend.birthday.day,
        )

        months.append(
            {
                "name": month_names[month_number],
                "friends": friends_in_month,
            }
        )

    friends_with_birthdays = list(Friend.objects.exclude(birthday__isnull=True))
    upcoming_birthdays = sorted(
        friends_with_birthdays,
        key=lambda friend: friend.days_until_birthday,
    )[:8]

    context = {
        "months": months,
        "upcoming_birthdays": upcoming_birthdays,
    }

    return render(request, "friends/birthday_calendar.html", context)


def zodiac_dashboard(request):
    zodiac_counts = list(
        Friend.objects.exclude(zodiac="")
        .values("zodiac")
        .annotate(total=Count("id"))
        .order_by("-total", "zodiac")
    )

    most_common = zodiac_counts[0]["zodiac"] if zodiac_counts else "Not enough data yet"

    context = {
        "zodiac_counts": zodiac_counts,
        "most_common": most_common,
    }

    return render(request, "friends/zodiac_dashboard.html", context)


def mbti_dashboard(request):
    mbti_counts = list(
        Friend.objects.exclude(mbti="")
        .values("mbti")
        .annotate(total=Count("id"))
        .order_by("-total", "mbti")
    )

    most_common = mbti_counts[0]["mbti"] if mbti_counts else "Not enough data yet"

    context = {
        "mbti_counts": mbti_counts,
        "most_common": most_common,
    }

    return render(request, "friends/mbti_dashboard.html", context)


def statistics(request):
    tier_labels = dict(Friend.TIER_CHOICES)
    morning_labels = dict(Friend.MORNING_NIGHT_CHOICES)

    tier_counts = list(
        Friend.objects.values("tier")
        .annotate(total=Count("id"))
        .order_by("-total")
    )

    for row in tier_counts:
        row["label"] = tier_labels.get(row["tier"], row["tier"])

    connection_counts = list(
        Friend.objects.values("connection_group__name")
        .annotate(total=Count("id"))
        .order_by("-total")
    )

    colour_counts = list(
        Friend.objects.exclude(favourite_colour="")
        .values("favourite_colour")
        .annotate(total=Count("id"))
        .order_by("-total", "favourite_colour")
    )

    season_counts = list(
        Friend.objects.exclude(favourite_season="")
        .values("favourite_season")
        .annotate(total=Count("id"))
        .order_by("-total", "favourite_season")
    )

    morning_night_counts = list(
        Friend.objects.exclude(morning_or_night="")
        .values("morning_or_night")
        .annotate(total=Count("id"))
        .order_by("-total", "morning_or_night")
    )

    for row in morning_night_counts:
        row["label"] = morning_labels.get(row["morning_or_night"], row["morning_or_night"])

    context = {
        "tier_counts": tier_counts,
        "connection_counts": connection_counts,
        "colour_counts": colour_counts,
        "season_counts": season_counts,
        "morning_night_counts": morning_night_counts,
    }

    return render(request, "friends/statistics.html", context)


def search(request):
    form = SearchForm(request.GET or None)
    query = ""

    friend_results = Friend.objects.none()
    memory_results = Memory.objects.none()

    if form.is_valid():
        query = form.cleaned_data.get("query", "").strip()

        if query:
            friend_results = Friend.objects.filter(
                Q(first_name__icontains=query)
                | Q(last_name__icontains=query)
                | Q(nickname__icontains=query)
                | Q(how_we_met__icontains=query)
                | Q(favourite_colour__icontains=query)
                | Q(favourite_food__icontains=query)
                | Q(favourite_restaurant__icontains=query)
                | Q(favourite_season__icontains=query)
                | Q(hobbies__icontains=query)
                | Q(sports_team__icontains=query)
                | Q(notes__icontains=query)
                | Q(mbti__icontains=query)
                | Q(zodiac__icontains=query)
                | Q(connection_group__name__icontains=query)
            ).distinct()

            memory_results = Memory.objects.filter(
                Q(title__icontains=query)
                | Q(description__icontains=query)
                | Q(location_name__icontains=query)
                | Q(mood__icontains=query)
                | Q(tags__icontains=query)
                | Q(friends__first_name__icontains=query)
                | Q(friends__last_name__icontains=query)
                | Q(friends__nickname__icontains=query)
            ).distinct()

    context = {
        "form": form,
        "query": query,
        "friend_results": friend_results,
        "memory_results": memory_results,
    }

    return render(request, "friends/search.html", context)