import click
from rich.console import Console
from pyfiglet import figlet_format
from .weather import get_weather_alert
from .news import get_news_alerts

console = Console()

def show_banner():
    banner = figlet_format("LiveAlert", font="small")
    console.print(f"[bold cyan]{banner}[/bold cyan]")
    console.print("Real-time Weather and News Alerts\n", style="bold yellow")

@click.group(invoke_without_command=True)
@click.pass_context
def main(ctx):
    """Real-time weather and news alert system"""
    if ctx.invoked_subcommand is None:
        show_banner()
        console.print("Please specify a command:\n", style="bold")
        console.print("  livealert weather [city]", style="green")
        console.print("  livealert news [count]\n", style="green")

@main.command()
@click.argument('city')
def weather(city):
    """Get real-time weather alerts for a city"""
    try:
        get_weather_alert(city)
    except Exception as e:
        console.print(f"[red]⚠️ Alert Error: {e}[/red]")

@main.command()
@click.argument('count', type=int, required=False, default=5)
def news(count):
    """Get breaking news alerts"""
    try:
        get_news_alerts(count)
    except Exception as e:
        console.print(f"[red]⚠️ Alert Error: {e}[/red]")
