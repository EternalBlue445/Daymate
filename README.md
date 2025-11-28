# How does it work?
1. Frontend makes a GET request on /api/weather/{city}. Ex: /api/weather/dhaka
2. django receives that request
   - fetches the weather data from "https://www.accuweather.com" with API call.
   - Then the django fetches the news article from The daily star and jugantor
   - Then django combines the weather data and news article and sends it to Gemini and gets the recommendation
   - 
# Screenshots
## Location
![Location](Screenshots/location.png)

## Local News
![News](Screenshots/news.png)

## Recommendation
![Recommendation](Screenshots/recom.png)
