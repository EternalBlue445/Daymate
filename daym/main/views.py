# views.py
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated, AllowAny, IsAuthenticatedOrReadOnly
from rest_framework.response import Response
from django.core.cache import cache
from .scrape import get_weather_details, get_link
from .news import LocalNews
from .ocr_gemini import Gemini


CACHE_TTL = 4 * 3600

def all_task(location):
    loc_key = location.strip().lower()

    weather_key = f"weather:{loc_key}"
    news_key = f"news:{loc_key}"
    rec_key = f"rec:{loc_key}"
    combined_key = f"combined:{loc_key}"

    cached = cache.get(combined_key)
    if cached:
        return cached

    weather_data = cache.get(weather_key)
    if not weather_data:
        try:
            link = get_link(location)
            weather_data = get_weather_details(link)
        except:
            weather_data = {}
        cache.set(weather_key, weather_data, CACHE_TTL)


    news_list = cache.get(news_key)
    if not news_list:
        try:
            ln = LocalNews()
            news_list = ln.collect_all()
        except:
            news_list = []
        cache.set(news_key, news_list, CACHE_TTL)


    recommendation = cache.get(rec_key)
    if not recommendation:
        try:
            gem = Gemini()
            data_for_recom = {
                "weather": weather_data,
                "news": news_list,
                "location": location
            }
            recommendation = gem.recom(data_for_recom, "Bangla")
        except:
            recommendation = ""
        cache.set(rec_key, recommendation, CACHE_TTL)

    combined = {
        "current": weather_data.get("current", {}),
        "hourly": weather_data.get("hourly", []),
        "daily7": weather_data.get("daily7", []),
        "aqi": weather_data.get("aqi", None),
        "news": news_list,
        "recommendation": recommendation
    }
    with open("ok.txt","w",encoding="utf-8") as f:
        f.write(str(combined))
    cache.set(combined_key, combined, CACHE_TTL)
    return combined

@api_view(['GET'])
@permission_classes([IsAuthenticatedOrReadOnly])
def weather_api(request, location):
    result = all_task(location)
    return Response(result)
