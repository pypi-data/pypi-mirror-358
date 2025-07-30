import os
import requests
from rich.console import Console
from rich.table import Table
from dotenv import load_dotenv

load_dotenv()
console = Console()

def get_weather_alert(city):
    api_key = os.getenv("OPENWEATHER_API_KEY")
    response = requests.get(
        "https://api.openweathermap.org/data/2.5/weather",
        params={
            'q': city,
            'appid': api_key,
            'units': 'metric'
        }
    )
    data = response.json()
    
    table = Table(title=f"Weather Alert for {city}")
    table.add_column("Metric", style="cyan")
    table.add_column("Value", style="magenta")
    
    table.add_row("Temperature", f"{data['main']['temp']}°C")
    table.add_row("Conditions", data['weather'][0]['description'])
    table.add_row("Humidity", f"{data['main']['humidity']}%")
    
    console.print(table)