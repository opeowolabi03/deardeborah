from django.urls import path

from . import views

app_name = "friends"

urlpatterns = [
    path("", views.home, name="home"),

    path("friends/", views.friend_directory, name="friend_directory"),
    path("friends/add/", views.add_friend, name="add_friend"),
    path("friends/<int:pk>/", views.friend_profile, name="friend_profile"),

    path("memories/", views.memories, name="memories"),
    path("memories/<int:pk>/", views.memory_detail, name="memory_detail"),
    path("memory-map/", views.memory_map, name="memory_map"),

    path("birthdays/", views.birthday_calendar, name="birthday_calendar"),

    path("zodiac/", views.zodiac_dashboard, name="zodiac_dashboard"),
    path("mbti/", views.mbti_dashboard, name="mbti_dashboard"),
    path("statistics/", views.statistics, name="statistics"),

    path("search/", views.search, name="search"),
]