import os
import requests
from rich.console import Console
from rich.table import Table
from dotenv import load_dotenv

load_dotenv()
console = Console()

def get_news_alerts(count=5):
    api_key = os.getenv("NEWSAPI_API_KEY")
    response = requests.get(
        "https://newsapi.org/v2/top-headlines",
        params={
            'apiKey': api_key,
            'pageSize': count,
            'country': 'us'
        }
    )
    data = response.json()
    
    table = Table(title="News Alerts")
    table.add_column("Title", style="cyan")
    table.add_column("Source", style="magenta")
    
    for article in data['articles']:
        table.add_row(article['title'], article['source']['name'])
    
    console.print(table)