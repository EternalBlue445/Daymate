# Frameworks Used
1. Frontend: ReactJs (https://github.com/EternalBlue445/Daymate.git)
2. Backend: Django  (https://github.com/EternalBlue445/Daymate-django.git)


# Live Urls 
 - Frontend(live):  https://daymate-s7gj.onrender.com
 - Backend(live):  https://daymate-django.onrender.com

# Screenshot
![Daymate](Screenshots/daymate.png)

# How does it work?
1. Frontend makes a GET request on https://daymate-django.onrender.com/api/weather/{city}. Ex: /api/weather/dhaka
2. django receives that request
   - fetches the weather data from "https://www.accuweather.com" with API call for that specific city.
   - Then the django fetches the news article from The daily star and jugantor
   - Then django combines the weather data and news article and sends it to Gemini and gets the recommendation
   - Finally, the weather data,news article and recommendation are sent to the frontend as a JSON Response.

# Workflow
   - Frontend hits api (/api/weather/{any_city}) 
   - Backend receives it and fetches weather data for that city & local news articles 
   - sends the combined data to Gemini 
   - returns {weather data,local news and recommendation from Gemini} to frontend

# It takes 1 or 2 minutes to load the server.
## If you see this following screen, dont't worry, wait for 1 minute. It will load the server. 
![Loading](Screenshots/Loading.png)

# How to use it? 
   - Render is a free hosting platform, so upon inactivity it suspends the server(frontend and backend).
   - So, go to the Backend url first and then frontend.
   - Wait for 1 minute. Render will then restart the servers. When backend and frontend both are running then change locations to see new recommendations.

# How you gonna know that backend is running?
   - Backend has 2 endpoints ('/','api/weather/{city}')
   - So, to see if it is running or not just go to -> "https://daymate-django.onrender.com/" will return -> {"status": "running", "message": "API is live!"} this json response.

# Screenshots
## Location
![Location](Screenshots/location.png)

## Local News
![News](Screenshots/news.png)

## Recommendation
![Recommendation](Screenshots/recom.png)
