import requests


def get_weather(city="Bengaluru"):

    try:

        url = "https://wttr.in/" + city + "?format=j1"

        response = requests.get(url, timeout=10)

        if response.status_code != 200:
            return "Sorry, I couldn't get the weather."

        data = response.json()

        current = data["current_condition"][0]

        temperature = current["temp_C"]
        feels_like = current["FeelsLikeC"]
        humidity = current["humidity"]
        description = current["weatherDesc"][0]["value"]

        weather = (
            f"The weather in {city} is {description}. "
            f"The temperature is {temperature} degrees Celsius. "
            f"It feels like {feels_like} degrees. "
            f"Humidity is {humidity} percent."
        )

        return weather

    except Exception as e:

        print("Weather Error:", e)

        return "Sorry, I couldn't get the weather right now."