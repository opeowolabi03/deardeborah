from collections import defaultdict

from django.db.models import Count, Q
from django.http import HttpResponse
from django.shortcuts import get_object_or_404, redirect
from django.utils.html import escape

from .forms import FriendForm, MemoryForm, SearchForm
from .models import ConnectionGroup, Friend, Memory, Photo


def _nav_html():
    return """
    <p>
        <a href="/">Home</a> |
        <a href="/friends/">Friend Directory</a> |
        <a href="/friends/add/">Add Friend</a> |
        <a href="/memories/">Memories</a> |
        <a href="/memory-map/">Memory Map</a> |
        <a href="/birthdays/">Birthday Calendar</a> |
        <a href="/zodiac/">Zodiac Dashboard</a> |
        <a href="/mbti/">MBTI Dashboard</a> |
        <a href="/statistics/">Statistics</a> |
        <a href="/search/">Search</a> |
        <a href="/admin/">Admin</a>
    </p>
    """


def _page(title, body):
    html = f"""
    <!doctype html>
    <html lang="en">
    <head>
        <meta charset="utf-8">
        <title>{escape(title)} | Dear Deborah</title>
    </head>
    <body>
        <h1>{escape(title)}</h1>
        {_nav_html()}
        <hr>
        {body}
    </body>
    </html>
    """
    return HttpResponse(html)


def _friend_link(friend):
    return f'<a href="{friend.get_absolute_url()}">{escape(friend.display_name)}</a>'


def _memory_link(memory):
    return f'<a href="{memory.get_absolute_url()}">{escape(memory.title)}</a>'


def _empty_message(message):
    return f"<p><em>{escape(message)}</em></p>"


def home(request):
    friend_count = Friend.objects.count()
    memory_count = Memory.objects.count()
    photo_count = Photo.objects.count()
    inner_circle_count = Friend.objects.filter(tier="inner_circle").count()

    recent_friends = Friend.objects.order_by("-created_at")[:5]

    friends_with_birthdays = [
        friend for friend in Friend.objects.exclude(birthday__isnull=True)
    ]
    upcoming_birthdays = sorted(
        friends_with_birthdays,
        key=lambda friend: friend.days_until_birthday,
    )[:5]

    recent_html = "".join(
        f"<li>{_friend_link(friend)} - added {friend.created_at.strftime('%d %b %Y')}</li>"
        for friend in recent_friends
    ) or "<li>No friends added yet.</li>"

    birthday_html = "".join(
        f"<li>{_friend_link(friend)} - {friend.days_until_birthday} days away</li>"
        for friend in upcoming_birthdays
    ) or "<li>No birthdays added yet.</li>"

    body = f"""
    <h2>Backend dashboard test</h2>
    <p>This confirms the Dear Deborah database is connected and queryable.</p>

    <ul>
        <li>Total friends: {friend_count}</li>
        <li>Inner Circle friends: {inner_circle_count}</li>
        <li>Total memories: {memory_count}</li>
        <li>Total photos: {photo_count}</li>
    </ul>

    <h2>Recently added friends</h2>
    <ul>{recent_html}</ul>

    <h2>Upcoming birthdays</h2>
    <ul>{birthday_html}</ul>
    """

    return _page("Dear Deborah Home", body)


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

    friend_html = "".join(
        f"""
        <li>
            {_friend_link(friend)}
            <br>Tier: {friend.get_tier_display()}
            <br>Connection: {escape(friend.connection_group.name) if friend.connection_group else "Not added"}
            <br>MBTI: {escape(friend.mbti) if friend.mbti else "Not added"}
            <br>Zodiac: {escape(friend.zodiac) if friend.zodiac else "Not added"}
        </li>
        <br>
        """
        for friend in friends
    ) or "<li>No friends found.</li>"

    groups = ConnectionGroup.objects.all()
    group_options = "".join(
        f'<option value="{group.id}">{escape(group.name)}</option>'
        for group in groups
    )

    body = f"""
    <h2>Friend Directory Backend Test</h2>

    <form method="get">
        <p>
            <label>Search:</label>
            <input type="text" name="q" value="{escape(query)}">
        </p>

        <p>
            <label>Tier:</label>
            <select name="tier">
                <option value="">All tiers</option>
                <option value="inner_circle">Inner Circle</option>
                <option value="friend">Friend</option>
                <option value="archive">Archive</option>
            </select>
        </p>

        <p>
            <label>Connection group:</label>
            <select name="connection_group">
                <option value="">All groups</option>
                {group_options}
            </select>
        </p>

        <button type="submit">Filter</button>
    </form>

    <h2>Results</h2>
    <ul>{friend_html}</ul>
    """

    return _page("Friend Directory", body)


def add_friend(request):
    if request.method == "POST":
        form = FriendForm(request.POST, request.FILES)

        if form.is_valid():
            friend = form.save()
            return redirect(friend.get_absolute_url())
    else:
        form = FriendForm()

    field_list = "".join(
        f"<li>{escape(field.label)} - field ready</li>"
        for field in form
    )

    body = f"""
    <h2>Add Friend Backend Test</h2>
    <p>The FriendForm is loading correctly. The styled add-friend page will use this form after the backend test passes.</p>

    <h3>Fields loaded from FriendForm</h3>
    <ul>{field_list}</ul>

    <p>For now, add test friends through <a href="/admin/">Admin</a> after creating your superuser.</p>
    """

    return _page("Add Friend", body)


def friend_profile(request, pk):
    friend = get_object_or_404(
        Friend.objects.select_related("connection_group"),
        pk=pk,
    )

    memories = friend.memories.all()[:10]
    photos = friend.photos.all()[:10]

    memory_html = "".join(
        f"<li>{_memory_link(memory)} - {escape(memory.location_name) if memory.location_name else 'No location added'}</li>"
        for memory in memories
    ) or "<li>No memories linked yet.</li>"

    photo_html = "".join(
        f"<li>{escape(photo.caption) if photo.caption else 'Photo without caption'}</li>"
        for photo in photos
    ) or "<li>No photos linked yet.</li>"

    extended_profile = getattr(friend, "extended_profile", None)

    if extended_profile:
        extended_html = f"""
        <ul>
            <li>Favourite song: {escape(extended_profile.favourite_song) if extended_profile.favourite_song else "Not added"}</li>
            <li>Favourite movie: {escape(extended_profile.favourite_movie) if extended_profile.favourite_movie else "Not added"}</li>
            <li>Favourite show: {escape(extended_profile.favourite_show) if extended_profile.favourite_show else "Not added"}</li>
            <li>Dream trip: {escape(extended_profile.dream_trip) if extended_profile.dream_trip else "Not added"}</li>
        </ul>
        """
    else:
        extended_html = _empty_message("No extended profile added yet.")

    body = f"""
    <h2>{escape(friend.display_name)}</h2>

    <ul>
        <li>Tier: {friend.get_tier_display()}</li>
        <li>Birthday: {friend.birthday if friend.birthday else "Not added"}</li>
        <li>Age: {friend.age if friend.age is not None else "Not added"}</li>
        <li>Days until birthday: {friend.days_until_birthday if friend.days_until_birthday is not None else "Not added"}</li>
        <li>Connection group: {escape(friend.connection_group.name) if friend.connection_group else "Not added"}</li>
        <li>Favourite colour: {escape(friend.favourite_colour) if friend.favourite_colour else "Not added"}</li>
        <li>Favourite food: {escape(friend.favourite_food) if friend.favourite_food else "Not added"}</li>
        <li>MBTI: {escape(friend.mbti) if friend.mbti else "Not added"}</li>
        <li>Zodiac: {escape(friend.zodiac) if friend.zodiac else "Not added"}</li>
        <li>Sports team: {escape(friend.sports_team) if friend.sports_team else "Not added"}</li>
    </ul>

    <h2>How you met</h2>
    <p>{escape(friend.how_we_met) if friend.how_we_met else "Not added"}</p>

    <h2>Hobbies</h2>
    <p>{escape(friend.hobbies) if friend.hobbies else "Not added"}</p>

    <h2>Notes</h2>
    <p>{escape(friend.notes) if friend.notes else "Not added"}</p>

    <h2>Extended profile</h2>
    {extended_html}

    <h2>Memories</h2>
    <ul>{memory_html}</ul>

    <h2>Photos</h2>
    <ul>{photo_html}</ul>
    """

    return _page(friend.display_name, body)


def memories(request):
    all_memories = Memory.objects.prefetch_related("friends").all()

    memory_html = ""

    for memory in all_memories:
        friend_names = ", ".join(friend.display_name for friend in memory.friends.all())
        memory_html += f"""
        <li>
            {_memory_link(memory)}
            <br>Date: {memory.date if memory.date else "Not added"}
            <br>Location: {escape(memory.location_name) if memory.location_name else "Not added"}
            <br>Friends: {escape(friend_names) if friend_names else "No friends linked"}
        </li>
        <br>
        """

    if not memory_html:
        memory_html = "<li>No memories added yet.</li>"

    body = f"""
    <h2>Memories Backend Test</h2>
    <p>This page lists memories stored in the database.</p>
    <ul>{memory_html}</ul>
    """

    return _page("Memories", body)


def memory_detail(request, pk):
    memory = get_object_or_404(Memory.objects.prefetch_related("friends", "photos"), pk=pk)

    friend_links = "".join(
        f"<li>{_friend_link(friend)}</li>"
        for friend in memory.friends.all()
    ) or "<li>No friends linked.</li>"

    photo_list = "".join(
        f"<li>{escape(photo.caption) if photo.caption else 'Photo without caption'}</li>"
        for photo in memory.photos.all()
    ) or "<li>No photos linked.</li>"

    body = f"""
    <h2>{escape(memory.title)}</h2>

    <ul>
        <li>Date: {memory.date if memory.date else "Not added"}</li>
        <li>Location: {escape(memory.location_name) if memory.location_name else "Not added"}</li>
        <li>Latitude: {memory.latitude if memory.latitude is not None else "Not added"}</li>
        <li>Longitude: {memory.longitude if memory.longitude is not None else "Not added"}</li>
        <li>Mood: {escape(memory.mood) if memory.mood else "Not added"}</li>
        <li>Tags: {escape(memory.tags) if memory.tags else "Not added"}</li>
        <li>Favourite memory: {"Yes" if memory.is_favourite else "No"}</li>
    </ul>

    <h2>Description</h2>
    <p>{escape(memory.description)}</p>

    <h2>Friends involved</h2>
    <ul>{friend_links}</ul>

    <h2>Photos</h2>
    <ul>{photo_list}</ul>
    """

    return _page(memory.title, body)


def memory_map(request):
    memories_with_locations = Memory.objects.exclude(location_name="").prefetch_related("friends")

    memory_html = ""

    for memory in memories_with_locations:
        friend_names = ", ".join(friend.display_name for friend in memory.friends.all())

        memory_html += f"""
        <li>
            {_memory_link(memory)}
            <br>Pin location: {escape(memory.location_name)}
            <br>Coordinates: {memory.latitude if memory.latitude is not None else "No latitude"}, {memory.longitude if memory.longitude is not None else "No longitude"}
            <br>Friends involved: {escape(friend_names) if friend_names else "No friends linked"}
        </li>
        <br>
        """

    if not memory_html:
        memory_html = "<li>No map memories added yet. Add memories with a location name in Admin.</li>"

    body = f"""
    <h2>Memory Map Backend Test</h2>
    <p>This confirms that memory locations can be stored and listed before the interactive map UI is added.</p>
    <ul>{memory_html}</ul>
    """

    return _page("Memory Map", body)


def birthday_calendar(request):
    month_groups = defaultdict(list)

    friends = Friend.objects.exclude(birthday__isnull=True)

    for friend in friends:
        month_number = friend.birthday.month
        month_groups[month_number].append(friend)

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

    calendar_html = ""

    for month_number in range(1, 13):
        friends_in_month = sorted(
            month_groups[month_number],
            key=lambda friend: friend.birthday.day,
        )

        friend_items = "".join(
            f"<li>{friend.birthday.day}: {_friend_link(friend)}</li>"
            for friend in friends_in_month
        ) or "<li>No birthdays.</li>"

        calendar_html += f"""
        <h3>{month_names[month_number]}</h3>
        <ul>{friend_items}</ul>
        """

    friends_with_birthdays = [
        friend for friend in Friend.objects.exclude(birthday__isnull=True)
    ]

    upcoming_birthdays = sorted(
        friends_with_birthdays,
        key=lambda friend: friend.days_until_birthday,
    )[:5]

    upcoming_html = "".join(
        f"<li>{_friend_link(friend)} - {friend.days_until_birthday} days away</li>"
        for friend in upcoming_birthdays
    ) or "<li>No upcoming birthdays.</li>"

    body = f"""
    <h2>Next birthdays</h2>
    <ul>{upcoming_html}</ul>

    <h2>Birthdays by month</h2>
    {calendar_html}
    """

    return _page("Birthday Calendar", body)


def zodiac_dashboard(request):
    zodiac_counts = (
        Friend.objects.exclude(zodiac="")
        .values("zodiac")
        .annotate(total=Count("id"))
        .order_by("-total", "zodiac")
    )

    rows = "".join(
        f"<li>{escape(row['zodiac'])}: {row['total']}</li>"
        for row in zodiac_counts
    ) or "<li>No zodiac data added yet.</li>"

    most_common = zodiac_counts[0]["zodiac"] if zodiac_counts else "Not enough data yet"

    body = f"""
    <h2>Zodiac Backend Test</h2>
    <p>Most common sign: {escape(most_common)}</p>
    <ul>{rows}</ul>
    """

    return _page("Zodiac Dashboard", body)


def mbti_dashboard(request):
    mbti_counts = (
        Friend.objects.exclude(mbti="")
        .values("mbti")
        .annotate(total=Count("id"))
        .order_by("-total", "mbti")
    )

    rows = "".join(
        f"<li>{escape(row['mbti'])}: {row['total']}</li>"
        for row in mbti_counts
    ) or "<li>No MBTI data added yet.</li>"

    most_common = mbti_counts[0]["mbti"] if mbti_counts else "Not enough data yet"

    body = f"""
    <h2>MBTI Backend Test</h2>
    <p>Most common MBTI type: {escape(most_common)}</p>
    <ul>{rows}</ul>
    """

    return _page("MBTI Dashboard", body)


def statistics(request):
    tier_counts = Friend.objects.values("tier").annotate(total=Count("id")).order_by("-total")
    connection_counts = (
        Friend.objects.values("connection_group__name")
        .annotate(total=Count("id"))
        .order_by("-total")
    )
    colour_counts = (
        Friend.objects.exclude(favourite_colour="")
        .values("favourite_colour")
        .annotate(total=Count("id"))
        .order_by("-total", "favourite_colour")
    )
    season_counts = (
        Friend.objects.exclude(favourite_season="")
        .values("favourite_season")
        .annotate(total=Count("id"))
        .order_by("-total", "favourite_season")
    )
    morning_night_counts = (
        Friend.objects.exclude(morning_or_night="")
        .values("morning_or_night")
        .annotate(total=Count("id"))
        .order_by("-total", "morning_or_night")
    )

    tier_labels = dict(Friend.TIER_CHOICES)
    morning_labels = dict(Friend.MORNING_NIGHT_CHOICES)

    tier_html = "".join(
        f"<li>{escape(tier_labels.get(row['tier'], row['tier']))}: {row['total']}</li>"
        for row in tier_counts
    ) or "<li>No tier data.</li>"

    connection_html = "".join(
        f"<li>{escape(row['connection_group__name'] or 'No connection group')}: {row['total']}</li>"
        for row in connection_counts
    ) or "<li>No connection data.</li>"

    colour_html = "".join(
        f"<li>{escape(row['favourite_colour'])}: {row['total']}</li>"
        for row in colour_counts
    ) or "<li>No colour data.</li>"

    season_html = "".join(
        f"<li>{escape(row['favourite_season'])}: {row['total']}</li>"
        for row in season_counts
    ) or "<li>No season data.</li>"

    morning_night_html = "".join(
        f"<li>{escape(morning_labels.get(row['morning_or_night'], row['morning_or_night']))}: {row['total']}</li>"
        for row in morning_night_counts
    ) or "<li>No morning/night data.</li>"

    body = f"""
    <h2>Statistics Backend Test</h2>

    <h3>Friendship tiers</h3>
    <ul>{tier_html}</ul>

    <h3>Connection groups</h3>
    <ul>{connection_html}</ul>

    <h3>Favourite colours</h3>
    <ul>{colour_html}</ul>

    <h3>Favourite seasons</h3>
    <ul>{season_html}</ul>

    <h3>Morning vs Night</h3>
    <ul>{morning_night_html}</ul>
    """

    return _page("Statistics", body)


def search(request):
    form = SearchForm(request.GET or None)
    query = ""

    if form.is_valid():
        query = form.cleaned_data.get("query", "").strip()

    friend_results = Friend.objects.none()
    memory_results = Memory.objects.none()

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

    friend_html = "".join(
        f"<li>{_friend_link(friend)} - {friend.get_tier_display()}</li>"
        for friend in friend_results
    ) or "<li>No friend results yet.</li>"

    memory_html = "".join(
        f"<li>{_memory_link(memory)} - {escape(memory.location_name) if memory.location_name else 'No location added'}</li>"
        for memory in memory_results
    ) or "<li>No memory results yet.</li>"

    body = f"""
    <h2>Search Backend Test</h2>

    <form method="get">
        <label>Search the friendship database:</label>
        <input type="text" name="query" value="{escape(query)}">
        <button type="submit">Search</button>
    </form>

    <h2>Friend results</h2>
    <ul>{friend_html}</ul>

    <h2>Memory results</h2>
    <ul>{memory_html}</ul>
    """

    return _page("Search", body)