import requests as rq
import os
from bs4 import BeautifulSoup

def get_link(name):
    api_key = os.environ["Accu_api"]
    city = name.replace(" ", "+")
    location_id_url = "https://dataservice.accuweather.com/locations/v1/cities/search"
    params = {"q": city}
    headers = {"Authorization": f"Bearer {api_key}"}

    res = rq.get(location_id_url, params=params, headers=headers)

    if res.status_code == 200:
        data = res.json()
        if data:
            Key = data[0]["Key"]
            weather_url = f"https://dataservice.accuweather.com/currentconditions/v1/{Key}"
            weather = rq.get(weather_url, headers=headers)
            link = weather.json()[0]["Link"].replace("current-weather","weather-forecast")
            return link
            
        else:
            print("No data found for this city")
    else:
        print(f"failed {res.status_code}")
    return ""

def get_weather_details(link):
    #link = "https://www.accuweather.com/en/bd/rajshahi/30529/weather-forecast/30529"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
        "Accept-Language": "en-US,en;q=0.5"
    }
    response = rq.get(link, headers=headers)
    soup = BeautifulSoup(response.text, 'html.parser')
    
    # Current weather
    card = soup.find('div', class_='cur-con-weather-card__body')
    current = {
        "temp": card.find('div', class_='temp').text.strip(),
        "condition": card.find('span', class_='phrase').text.strip(),
        "wind": card.find_all('div', class_='spaced-content')[1].find('span', class_='value').text.strip(),
        "aqi": card.find_all('div', class_='spaced-content')[2].find('span', class_='value').text.strip(),
        "icon": "https://www.accuweather.com" + card.find('svg', class_='weather-icon')['data-src']
    }
    
    # Hourly
    hourly_items = soup.find_all('a', class_='hourly-list__list__item')
    hourly = []
    for item in hourly_items[:]:
        hourly.append({
            "time": item.find('span', class_='hourly-list__list__item-time').text.strip(),
            "condition": item.find('img', class_='hourly-list__list__item-icon')['src'],
            "temp": item.find('span', class_='hourly-list__list__item-temp').text.strip()
        })
    
    # Daily
    daily_items = soup.find_all('a', class_='daily-list-item')
    daily7 = []
    for item in daily_items:
        daily7.append({
            "day": item.find('p', class_='day').text.strip(),
            "date": item.find('p').text.strip(),
            "icon": item.find('img', class_='icon')['src'],
            "high": item.find('span', class_='temp-hi').text.strip(),
            "low": item.find('span', class_='temp-lo').text.strip(),
            "condition": item.find('div', class_='phrase').find('p', class_='no-wrap').text.strip()
        })
    
    return {
        "current": current,
        "hourly": hourly,
        "daily7": daily7[1:8],  
     #   "aqi": {"value": current["air_quality"]},
        "recommendation": "Stay hydrated during humid conditions"
    }
