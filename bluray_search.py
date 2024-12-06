import os
import inquirer
from rich.console import Console
from rich.panel import Panel
import requests
from bs4 import BeautifulSoup
import re
from urllib.parse import quote
import psutil

console = Console()

# Standard resolution mappings
STANDARD_RESOLUTIONS = {
    # 4K resolutions
    "4K": {
        1.33: (3840, 2880, "4:3"),
        1.37: (3840, 2792, "Academy"),
        1.66: (3840, 2304, "5:3"),
        1.78: (3840, 2160, "16:9"),
        1.85: (3840, 2074, "Flat"),
        1.90: (3840, 2020, "DCI"),
        2.00: (3840, 1920, "2:1"),
        2.35: (3840, 1634, "Scope"),
        2.37: (3840, 1620, "64:27"),
        2.39: (3840, 1608, "DCI Scope"),
        2.40: (3840, 1600, "Scope"),
        2.44: (3840, 1572, "Wide Scope")
    },
    "HD": {
        1.33: (1920, 1440, "4:3"),
        1.37: (1920, 1396, "Academy"),
        1.66: (1920, 1152, "5:3"),
        1.78: (1920, 1080, "16:9"),
        1.85: (1920, 1036, "Flat"),
        1.90: (1920, 1010, "DCI"),
        2.00: (1920, 960, "2:1"),
        2.35: (1920, 816, "Scope"),
        2.37: (1920, 810, "64:27"),
        2.39: (1920, 804, "DCI Scope"),
        2.40: (1920, 800, "Blu-Ray Scope"),
        2.44: (1920, 786, "Wide Scope")
    }
}

def generate_usage_bars():
    """Generate and display system usage bars"""
    bar_length = 30
    default_bar_color = "#9656ce"
    high_usage_color = "#FF0000"
    
    # Get memory and CPU usage
    mem = psutil.virtual_memory()
    mem_usage = mem.percent
    cpu_usage = psutil.cpu_percent()
    
    # Set colors based on usage
    mem_bar_color = default_bar_color if mem_usage <= 90 else high_usage_color
    cpu_bar_color = default_bar_color if cpu_usage <= 90 else high_usage_color
    
    # Generate memory bar
    mem_filled = f"[{mem_bar_color}]/[/{mem_bar_color}]" * int(bar_length * mem_usage // 100)
    mem_empty = "[white]/[/white]" * (bar_length - int(bar_length * mem_usage // 100))
    mem_bar = f"[ {mem_filled}{mem_empty} ]"
    
    # Generate CPU bar
    cpu_filled = f"[{cpu_bar_color}]/[/{cpu_bar_color}]" * int(bar_length * cpu_usage // 100)
    cpu_empty = "[white]/[/white]" * (bar_length - int(bar_length * cpu_usage // 100))
    cpu_bar = f"[ {cpu_filled}{cpu_empty} ]"
    
    # Display bars
    percentage_color = "#5865F2"
    console.print(f"Mem% -= {mem_bar} =- [bold {percentage_color}]{mem_usage:.2f}%[/bold {percentage_color}]")
    console.print(f"CPU% -= {cpu_bar} =- [bold {percentage_color}]{cpu_usage:.2f}%[/bold {percentage_color}]")

def clear_screen():
    """Clear the terminal screen."""
    os.system('cls' if os.name == 'nt' else 'clear')

def search_bluray(movie_title):
    """Search Blu-ray.com for movie details"""
    console.print(Panel.fit("Searching Blu-ray.com...", title="Status"))
    
    try:
        # Check if input is a direct URL
        if movie_title.startswith('https://www.blu-ray.com'):
            url = movie_title
            details = get_movie_details(url)
        else:
            # Format search URL
            search_url = f"https://www.blu-ray.com/search/?quicksearch=1&quicksearch_country=all&quicksearch_keyword={quote(movie_title)}&section=bluraymovies"
            headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}
            
            # Perform initial search
            response = requests.get(search_url, headers=headers)
            response.raise_for_status()
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Find movie links
            movie_links = soup.find_all('a', href=re.compile(r'/movies/\d+/'))
            
            if not movie_links:
                console.print("[yellow]No results found[/yellow]")
                return
            
            # Create list of movies for user to choose from
            movies = []
            for link in movie_links[:5]:  # Limit to first 5 results
                title = link.get_text(strip=True)
                url = f"https://www.blu-ray.com{link['href']}"
                movies.append({'title': title, 'url': url})
            
            # Let user select movie
            questions = [
                inquirer.List('movie',
                    message='Select the correct movie',
                    choices=[m['title'] for m in movies] + ['Cancel Search'],
                )
            ]
            
            answer = inquirer.prompt(questions)
            
            if answer['movie'] == 'Cancel Search':
                return
            
            # Get selected movie URL
            selected_movie = next(m for m in movies if m['title'] == answer['movie'])
            details = get_movie_details(selected_movie['url'])
        
        console.print("\n[bold blue]══ Movie Details ════════[/bold blue]")
        if "Error" in details:
            console.print(f"[red]Error retrieving details: {details['Error']}[/red]")
        else:
            # Extract resolution and aspect ratio from video details
            resolution_match = re.search(r'Resolution:\s*(\d+p)', details["Video"])
            aspect_match = re.search(r'Aspect ratio:\s*(\d+\.?\d*):1', details["Video"])
            
            native_res = resolution_match.group(1) if resolution_match else "Unknown"
            aspect = float(aspect_match.group(1)) if aspect_match else None
            
            console.print("\n[bold cyan]Source Information:[/bold cyan]")
            console.print(f"[yellow]Native Resolution:[/yellow] {native_res}")
            if aspect:
                console.print(f"[yellow]Encoded Aspect Ratio:[/yellow] {aspect:.2f}:1")
                
                # Find closest standard aspect ratio
                closest_aspect = min(STANDARD_RESOLUTIONS["4K"].keys(), 
                                   key=lambda x: abs(x - aspect))
                
                console.print("\n[bold magenta]Recommended Timeline Settings ✨[/bold magenta]")
                if native_res == "1080p":
                    res = STANDARD_RESOLUTIONS["HD"][2.37]  # Use 2.37 for 2.36 source
                    console.print(f"\n[green]HD Timeline Settings[/green]")
                    console.print(f"• Width: [bold]{res[0]}[/bold]")
                    console.print(f"• Height: [bold]{res[1]}[/bold]")
                    console.print(f"• Aspect: [bold]2.37:1[/bold] ({res[2]})")
                else:
                    res = STANDARD_RESOLUTIONS["4K"][closest_aspect]
                    console.print(f"\n[green]UHD Timeline Settings[/green]")
                    console.print(f"• Width: [bold]{res[0]}[/bold]")
                    console.print(f"• Height: [bold]{res[1]}[/bold]")
                    console.print(f"• Aspect: [bold]{closest_aspect:.2f}:1[/bold] ({res[2]})")
            
            # Display full technical details
            console.print("\n[bold blue]Full Technical Details[/bold blue]")
            console.print("\n[bold cyan]Video:[/bold cyan]")
            console.print(details["Video"])
            console.print("\n[bold cyan]Audio:[/bold cyan]")
            console.print(details["Audio"])
        
        input("\nPress Enter to continue...")
        
    except Exception as e:
        console.print(f"[red]Error searching Blu-ray.com: {str(e)}[/red]")
        input("\nPress Enter to continue...")

def get_movie_details(url):
    """Get technical details for a specific movie"""
    try:
        headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, 'html.parser')
        details = {}
        
        # Get Video details
        video_label = soup.find("span", class_="subheading", string="Video")
        if video_label:
            video_details = []
            sibling = video_label.find_next_sibling()
            while sibling and sibling.name == "br":
                if sibling.next_sibling and sibling.next_sibling.string:
                    video_details.append(sibling.next_sibling.string.strip())
                sibling = sibling.find_next_sibling()
            details["Video"] = "\n".join(video_details) if video_details else "N/A"
        else:
            details["Video"] = "N/A"
        
        # Get Audio details
        audio_label = soup.find("span", class_="subheading", string="Audio")
        if audio_label:
            audio_section = audio_label.find_next("div", id="shortaudio")
            details["Audio"] = audio_section.get_text(strip=True, separator="\n") if audio_section else "N/A"
        else:
            details["Audio"] = "N/A"
        
        return details
        
    except Exception as e:
        return {"Error": str(e)}

def main():
    while True:
        clear_screen()
        
        # Add usage bar display
        generate_usage_bars()
        
        # Add spacing and decorative elements
        console.print("\n[bright_black]═══════════════════════════════════════════════[/bright_black]")
        
        # Display welcome message with enhanced styling
        console.print(Panel.fit(
            "[bold blue]Blu-ray.com Search Tool[/bold blue]\n"
            "[cyan]Technical Specifications Lookup[/cyan]\n"
            "         [dim]Version 1.0[/dim]",
            title="[bold white]411[bold blue]Search[/bold blue][/bold white]",
            border_style="blue",
            padding=(1, 2),
            subtitle="[dim]Creator Edition[/dim]"
        ))
        
        console.print("[bright_black]═══════════════════════════════════════════════[/bright_black]\n")
        
        questions = [
            inquirer.Text('movie_title',
                message='Enter movie title to search (or "q" to quit)'
            )
        ]
        
        answer = inquirer.prompt(questions)
        if answer['movie_title'].lower() == 'q':
            console.print("Goodbye!", style="bold green")
            break
            
        search_bluray(answer['movie_title'])

if __name__ == "__main__":
    main()
