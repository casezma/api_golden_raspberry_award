from django.urls import path, include
from app.views import get_prize_interval_summary

urlpatterns = [
    path("api/v1/prizes_interval", get_prize_interval_summary,
         name="get_prize_interval_summary")
]
