# etsi/fliplist/utils.py

from rich.console import Console
from pyfiglet import Figlet

def print_banner():
    console = Console()
    fig = Figlet(font="slant")
    console.print(fig.renderText("fliplist"), style="bold green")
    console.print("🔁 etsi.fliplist – Reverse Anything. Cleanly.", style="cyan")
