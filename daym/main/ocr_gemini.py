from PIL import Image
import google.generativeai as genai
import os


class Gemini:
    def __init__(self):
        self.api_key = os.environ["GEMINI_API_KEY"] 
        self.model_name = 'gemini-2.5-flash'  
        self.initialize()
    
    def initialize(self):
        genai.configure(api_key=self.api_key)
        self.model = genai.GenerativeModel(self.model_name)

    def recom(self, weather_data, language):
        prompt = """You are an expert human weather advisor. Your job is to read the below json data and recommend.

        Input weather JSON(local news,next 12 hours data,current weather,location all of them mention in the data):
        {weather_data}

        Your recommendations must follow EXACT rules:

        FORMAT:
        - Each line must be an action a real climate expert would say with a small context.
        - No intro, no explanation, no conclusion

        LOGIC RULES:
        1. If AQI is "Poor" or "Unhealthy":
            → Include: "Wear a mask outdoors"
        2. If rain, heavy rain, storm, or thunderstorm in current or next 12 hours:
            → Include: "Carry an umbrella and avoid waterlogged areas"
        3. If temperature < 16°C:
            → Include: "Wear warm layers"
        4. If news reports nearby flooding, cyclone, landslide, tsunami, or severe weather warnings:
            → Include: a location-specific safety line, e.g.:
                - "Stay away from coastal areas"
                - "Avoid low-lying zones"
                - "Have emergency essentials ready"

        BEHAVIOR RULES:
        - Fill remaining lines with smart, human-like weather advice
        - Prioritize the most urgent risks first (disaster > storm > AQI > cold)
        - Never exceed 3 lines
        - Never repeat the same advice in different words
        - Keep tone like a real weather reporter giving quick guidance

        OUTPUT:
        At max the 3 advisory lines.
        """


        combined_input = f"\"{weather_data}\"\n\n{prompt} in {language}"
        response = self.model.generate_content([combined_input])
        return response.text

    def verify_connection(self):
        try:
            test_model = genai.GenerativeModel('gemini-flash') 
            response = test_model.generate_content("Test connection")
            return True
        except Exception as e:
            print(f"API connection verification failed: {str(e)}")
            return False

