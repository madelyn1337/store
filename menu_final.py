import os
import sys
from pathlib import Path
import inquirer
from rich.console import Console
from rich.panel import Panel
from rich import print as rprint
import ffmpeg
import requests
from bs4 import BeautifulSoup
import re
import urllib
from urllib.parse import quote
import xml.etree.ElementTree as ET
import subprocess
from rich.progress import Progress
import ffpb
import platform
import psutil
import ctypes
import time
import json
import zipfile
import shutil
import threading
import queue
import readline

console = Console()

class VideoProcessor:
    def __init__(self):
        self.supported_inputs = ['.mkv']
        self.supported_outputs = ['h265']
        self.base_dir = self.setup_directories()

    def strip_quotes(self, path: str) -> str:
        """Clean up file paths from drag & drop operations"""
        # Handle both Windows and Unix paths
        path = path.strip('"').strip("'")
        # Convert potential Windows backslashes to forward slashes
        return path.replace('\\', '/')

    def setup_directories(self):
        """Create required directory structure based on OS"""
        # Determine OS and set base videos/movies directory
        if platform.system() == 'Windows':
            videos_dir = Path.home() / 'Videos'
        else:  # macOS and others
            videos_dir = Path.home() / 'Movies'
        
        # Create 411 directory and subdirectories
        base_dir = videos_dir / '411'
        subdirs = ['proxies', 'scenepacks', 'media']
        
        try:
            # Create main directory if it doesn't exist
            base_dir.mkdir(exist_ok=True)
            
            # Create subdirectories
            for subdir in subdirs:
                (base_dir / subdir).mkdir(exist_ok=True)
            
            return base_dir
            
        except Exception as e:
            console.print(f"[red]Error creating directories: {str(e)}[/red]")
            return None

    def clear_screen(self):
        """Clear the terminal screen."""
        os.system('cls' if os.name == 'nt' else 'clear')

    def display_main_menu(self):
        while True:
            self.clear_screen()
            
            # Add usage bar display with enhanced styling
            self.generate_usage_bars()
            
            # Add spacing and decorative elements
            console.print("\n[bright_black]═══════════════════════════════════════════════[/bright_black]")
            
            # Display welcome message with enhanced styling
            console.print(Panel.fit(
                "[bold blue]Welcome to 411's ScenePack Tool[/bold blue]\n"
                "[cyan]Advanced Video Processing Suite[/cyan]\n"
                "         [dim]Version 1.0[/dim]",
                title="[bold white]411[bold blue]mpeg[/bold blue][/bold white]",
                border_style="blue",
                padding=(1, 2),
                subtitle="[dim]Creator Edition[/dim]"
            ))
            
            console.print("[bright_black]═══════════════════════════════════════════════[/bright_black]\n")
            
            # Enhanced menu options with icons and categories
            console.print("[bold white]┌─ Processing Tools[/bold white]")
            
            # Modify choices based on OS
            menu_choices = [
                'Installers & Uninstallers',
                'Encode Source',
                'EDL Export',
                'BluRay & WEB Info',
                'Timeline Settings',
                'Open Website',
                'Upgrade License',
                'Exit'
            ]

            # Add DMFS option only for Windows
            if platform.system() == "Windows":
                menu_choices.insert(3, 'DMFS Encoding Settings')
            else:
                # Add disabled DMFS option for non-Windows
                menu_choices.insert(3, 'DMFS Encoding Settings (Windows Only)')
            
            questions = [
                inquirer.List('choice',
                    message='What would you like to do?',
                    choices=menu_choices,
                )
            ]
            
            answer = inquirer.prompt(questions)
            
            # Skip DMFS on non-Windows
            if answer['choice'] == '[dim]DMFS Encoding Settings (Windows Only)[/dim]':
                console.print("[yellow]DMFS Encoding is only available on Windows systems.[/yellow]")
                time.sleep(2)
                continue
            
            if answer['choice'] == 'Installers & Uninstallers':
                if not is_admin():
                    console.print("Launching with admin privileges...")
                    if platform.system() == "Windows":
                        script = os.path.abspath(sys.argv[0])
                        params = f'"{script}" 1'  # Use "1" for installers menu
                        ctypes.windll.shell32.ShellExecuteW(None, "runas", sys.executable, params, None, 1)
                    else:
                        subprocess.Popen(['sudo', 'python3'] + sys.argv + ["1"])
                    time.sleep(1)
                    continue
                else:
                    self.installers_menu()
            elif answer['choice'] == 'DMFS Encoding Settings':
                self.set_preset()
            elif answer['choice'] == 'Encode Source':
                self.video_conversion_menu()
            elif answer['choice'] == 'Create Proxies':
                self.proxy_creator_menu()
            elif answer['choice'] == 'BluRay & WEB Info':
                self.bluray_search_menu()
            elif answer['choice'] == 'Timeline Settings':
                self.timeline_calculator_menu()
            elif answer['choice'] == 'EDL Export':
                self.edl_conform_menu()
            elif answer['choice'] == 'Open Website':
                self.open_website()
            elif answer['choice'] == 'Upgrade License':
                self.upgrade_license()
            else:
                console.print("Goodbye!", style="bold green")
                sys.exit(0)

    def generate_usage_bars(self):
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
        
        # Add disk usage bars
        if platform.system() == "Darwin":  # macOS specific handling
            try:
                # Get all mounted volumes
                partitions = psutil.disk_partitions(all=True)
                # Find the main system volume (usually the largest one)
                system_volume = None
                max_size = 0
                
                for partition in partitions:
                    try:
                        if partition.mountpoint == '/System/Volumes/Data':
                            system_volume = partition
                            break
                        usage = psutil.disk_usage(partition.mountpoint)
                        if usage.total > max_size:
                            max_size = usage.total
                            system_volume = partition
                    except (PermissionError, OSError):
                        continue
                
                if system_volume:
                    disk = psutil.disk_usage(system_volume.mountpoint)
                    disk_usage = disk.percent
                    disk_bar_color = default_bar_color if disk_usage <= 90 else high_usage_color
                    disk_filled = f"[{disk_bar_color}]/[/{disk_bar_color}]" * int(bar_length * disk_usage // 100)
                    disk_empty = "[white]/[/white]" * (bar_length - int(bar_length * disk_usage // 100))
                    disk_bar = f"[ {disk_filled}{disk_empty} ]"
                    console.print(
                        f"Macintosh HD% -= {disk_bar} =- [bold {percentage_color}]{disk_usage:.2f}%[/bold {percentage_color}]"
                    )
            except Exception as e:
                console.print(f"Macintosh HD - [bold red]Error: {str(e)}[/bold red]")
        else:  # Windows and other OS handling
            partitions = psutil.disk_partitions()
            for partition in partitions:
                try:
                    disk = psutil.disk_usage(partition.mountpoint)
                    disk_usage = disk.percent
                    disk_bar_color = default_bar_color if disk_usage <= 90 else high_usage_color
                    disk_filled = f"[{disk_bar_color}]/[/{disk_bar_color}]" * int(bar_length * disk_usage // 100)
                    disk_empty = "[white]/[/white]" * (bar_length - int(bar_length * disk_usage // 100))
                    disk_bar = f"[ {disk_filled}{disk_empty} ]"
                    console.print(
                        f"{partition.device}% -= {disk_bar} =- [bold {percentage_color}]{disk_usage:.2f}%[/bold {percentage_color}]"
                    )
                except PermissionError:
                    console.print(f"Drive {partition.device} - [bold red]Access Denied[/bold red]")

    def upgrade_license(self):
        self.clear_screen()
        if platform.system() == "Windows":
            os.system("start https://discord.gg/411")
        else:
            os.system("open https://discord.gg/411")

    def video_conversion_menu(self):
        while True:
            self.clear_screen()
            
            file_question = [
                inquirer.Text(
                    'input_file',
                    message='Drag & drop input video file (or enter path)',
                    validate=lambda _, x: Path(self.strip_quotes(x)).exists()
                )
            ]
            
            file_answer = inquirer.prompt(file_question)
            if not file_answer:  # Handle cancel/back
                return
            
            input_file = Path(self.strip_quotes(file_answer['input_file']))
            
            # Ask about EDL vs DMFS
            workflow_question = [
                inquirer.List('workflow',
                    message='Are you using EDL Export (Movies) or DMFS Encoding (TV Shows)?',
                    choices=['EDL Export', 'DMFS Encoding'],
                )
            ]
            workflow_answer = inquirer.prompt(workflow_question)
            if not workflow_answer:
                return

            # DMFS path - simple copy
            if workflow_answer['workflow'] == 'DMFS Encoding':
                name_question = [
                    inquirer.Text('output_name',
                        message='Enter output name (without extension)',
                        validate=lambda _, x: Path(self.strip_quotes(x)).exists()
                    )
                ]
                name_answer = inquirer.prompt(name_question)
                if not name_answer:
                    return
                    
                output_file = self.base_dir / 'media' / f"{name_answer['output_name']}.mp4"
                
                cmd = [
                    'ffmpeg',
                    '-i', str(input_file),
                    '-c', 'copy',
                    str(output_file)
                ]
                
                ffpb.main(argv=cmd[1:])  # Skip 'ffmpeg' in argv
                return

            # EDL path - full encode
            # Analyze source video
            try:
                probe = ffmpeg.probe(input_file)
                video_stream = next((stream for stream in probe['streams'] if stream['codec_type'] == 'video'), None)
                audio_streams = [stream for stream in probe['streams'] if stream['codec_type'] == 'audio']
                
                if not video_stream:
                    console.print("[red]No video stream found in input file[/red]")
                    return
            except Exception as e:
                console.print(f"[red]Error analyzing input file: {str(e)}[/red]")
                return

            # Get CPU info
            cpu_cores = psutil.cpu_count(logical=False)
            cpu_threads = psutil.cpu_count()
            
            # Determine encoding settings based on CPU
            preset = 'slow' if cpu_cores > 20 else 'medium'
            crf = 18 if cpu_cores > 20 else 20
            
            # Build x265 params based on CPU capability
            x265_params = [
                'profile=main10',
                f'pools={cpu_threads}',
                'frame-threads=4',
                'aq-mode=3',
                'psy-rd=1.0',
                'psy-rdoq=1.0',
                'rdoq-level=2',
                'no-sao=1'
            ]
            
            if cpu_cores > 20:
                x265_params.extend([
                    'rc-lookahead=60',
                    'ref=5',
                    'me=3',
                    'subme=5',
                    'b-adapt=2'
                ])
            else:
                x265_params.extend([
                    'rc-lookahead=40',
                    'ref=4',
                    'me=2',
                    'subme=4',
                    'b-adapt=1'
                ])

            questions = [
                inquirer.Confirm('auto_crop',
                    message='Enable automatic black bar detection?',
                    default=True
                ),
                inquirer.Confirm('tonemap',
                    message='Enable HDR to SDR conversion?',
                    default=False
                )
            ]
            
            answers = inquirer.prompt(questions)
            if not answers:
                return
            
            # Get output name
            name_question = [
                inquirer.Text('output_name',
                    message='Enter output name (without extension)',
                    # Remove the validate parameter since we don't need to validate if the path exists
                )
            ]
            
            name_answer = inquirer.prompt(name_question)
            if not name_answer:
                return
            
            output_file = self.base_dir / 'media' / f"{name_answer['output_name']}.mp4"
            
            # Check for HDR
            is_hdr = ('color_transfer' in video_stream and 'smpte2084' in video_stream['color_transfer'].lower()) or \
                     ('color_primaries' in video_stream and 'bt2020' in video_stream['color_primaries'].lower())
            if is_hdr:
                console.print("[yellow]HDR content detected[/yellow]")
            
            # Build FFmpeg command
            cmd = ['ffmpeg', '-i', str(input_file)]
            
            # Add crop if requested
            if answers['auto_crop']:
                crop_values = self.detect_black_bars(input_file)
                if crop_values:
                    w, h, x, y = crop_values
                    cmd.extend(['-vf', f'crop={w}:{h}:{x}:{y}'])
            
            # Add tonemapping if requested
            if answers['tonemap']:
                tonemap_filter = 'zscale=t=linear:npl=203,format=gbrpf32le,tonemap=reinhard:desat=0,zscale=p=709:t=709:m=709:r=limited:dither=error_diffusion,format=yuv420p,sidedata=delete'
                if 'crop' in cmd:
                    crop_idx = cmd.index('-vf') + 1
                    cmd[crop_idx] = f"{cmd[crop_idx]},{tonemap_filter}"
                else:
                    cmd.extend(['-vf', tonemap_filter])
            
            # Check for 5.1 audio and add center channel extraction
            surround_track = next((
                stream for stream in audio_streams 
                if stream.get('channels', 0) == 6
            ), None)
            
            if surround_track:
                cmd.extend(['-af', 'pan=stereo|c0=FC|c1=FC', '-c:a', 'aac', '-b:a', '576k'])
            else:
                cmd.extend(['-c:a', 'aac', '-b:a', '576k'])
            
            # Add video encoding parameters
            cmd.extend([
                '-c:v', 'libx265',
                '-preset', preset,
                '-crf', str(crf),
                '-x265-params', ':'.join(x265_params),
                '-threads', str(cpu_threads),
                str(output_file)
            ])
            
            # Now start the encoding with usage monitoring
            try:
                self.clear_screen()  # Clear screen once before starting
                # Add some initial spacing for the progress bar
                print("\n")
                console.print("[yellow]Encoding...[/yellow]")
                print("\n")
                
                # Create a thread to update usage bars
                stop_thread = threading.Event()
                usage_queue = queue.Queue()

                def update_usage():
                    while not stop_thread.is_set():
                        try:
                            # Save cursor position
                            print("\033[s", end="", flush=True)
                            
                            # Move to top
                            print("\033[H", end="", flush=True)
                            
                            # Display usage bars
                            self.generate_usage_bars()
                            
                            # Restore cursor position
                            print("\033[u", end="", flush=True)
                            
                            time.sleep(1)
                        except Exception as e:
                            usage_queue.put(e)
                            break

                # Start usage monitoring thread
                usage_thread = threading.Thread(target=update_usage)
                usage_thread.start()

                # Run ffpb command
                try:
                    ffpb.main(argv=cmd[1:])  # Skip 'ffmpeg' in argv
                finally:
                    # Stop usage monitoring thread
                    stop_thread.set()
                    usage_thread.join()

                    # Check for any errors from the usage thread
                    try:
                        error = usage_queue.get_nowait()
                        raise error
                    except queue.Empty:
                        pass

                console.print("[green]Encode completed successfully![/green]")

            except Exception as e:
                console.print(f"[red]Error during encoding: {str(e)}[/red]")

            input("\nPress Enter to continue...")
            self.clear_screen()
            return

    def bluray_search_menu(self):
        while True:
            self.clear_screen()
            questions = [
                inquirer.Text('movie_title',
                    message='Enter movie title to search'
                )
            ]
            
            answer = inquirer.prompt(questions)
            
            self.search_bluray(answer['movie_title'])

    def timeline_calculator_menu(self):
        while True:
            self.clear_screen()
            questions = [
                inquirer.Text(
                    'input_file',
                    message='Drag & drop video file for analysis (or enter path)',
                    validate=lambda _, x: Path(self.strip_quotes(x)).exists()
                ),
                inquirer.Confirm('auto_detect',
                    message='Auto-detect dimensions?',
                    default=True
                )
            ]
            
            answer = inquirer.prompt(questions)
            if not answer:
                return
            
            # Clean up input path
            answer['input_file'] = str(Path(self.strip_quotes(answer['input_file'])).resolve())
            
            if not answer['auto_detect']:
                manual_questions = [
                    inquirer.Text('original_width',
                        message='Enter original video width (pixels)',
                        validate=lambda _, x: x.isdigit()
                    ),
                    inquirer.Text('original_height',
                        message='Enter original video height (pixels)',
                        validate=lambda _, x: x.isdigit()
                    ),
                    inquirer.Text('crop_top',
                        message='Enter top crop amount (pixels)',
                        validate=lambda _, x: x.isdigit()
                    ),
                    inquirer.Text('crop_bottom',
                        message='Enter bottom crop amount (pixels)',
                        validate=lambda _, x: x.isdigit()
                    )
                ]
                manual_answers = inquirer.prompt(manual_questions)
                answer.update(manual_answers)
            
            self.calculate_timeline(answer)

    def process_video(self, options):
        """Process video with selected options"""
        try:
            input_file = options['input_file']
            
            self.clear_screen()
            # Check if input is HDR
            is_hdr = self.detect_hdr(input_file)
            if is_hdr:
                console.print("[yellow]HDR content detected[/yellow]")
            
            # Get output filename
            questions = [
                inquirer.Text('output_name',
                    message='Enter output name without extension (press Enter to use input name)',
                    default='',
                )
            ]
            
            answer = inquirer.prompt(questions)
            self.clear_screen()
            
            if answer['output_name'].strip():
                output_file = Path(input_file).parent / f"{answer['output_name']}.mkv"
            else:
                output_file = Path(input_file).with_suffix('.mkv')
            
            # Get encoding quality
            quality_questions = [
                inquirer.List('quality',
                    message='Select encoding quality',
                    choices=list(self.encoding_presets['H.265'].keys())
                )
            ]
            
            quality_answer = inquirer.prompt(quality_questions)
            self.clear_screen()
            
            encoding_preset = self.encoding_presets['H.265'][quality_answer['quality']]
            
            # Process video
            crop_values = None
            if options['auto_crop']:
                console.print("Detecting black bars...")
                crop_values = self.detect_black_bars(input_file)
                self.clear_screen()
                
                if crop_values:
                    w, h, x, y = crop_values
                    console.print(f"\n[green]Detected crop values: {w}:{h}:{x}:{y}[/green]")
                else:
                    console.print("\n[yellow]No black bars detected[/yellow]")
            
            if is_hdr and options.get('convert_sdr', False):
                self.convert_hdr_to_sdr(input_file, output_file, encoding_preset, crop_values)
            else:
                self.convert_video(input_file, output_file, encoding_preset, crop_values)
            
            self.clear_screen()
            console.print("[green]Video processing completed successfully![/green]")
            input("\nPress Enter to continue...")
            self.clear_screen()
            
        except Exception as e:
            self.clear_screen()
            console.print(f"[red]Error processing video: {str(e)}[/red]")
            input("\nPress Enter to continue...")
            self.clear_screen()

    def detect_hdr(self, input_file):
        """Check if video stream contains HDR metadata"""
        try:
            # Use subprocess to run ffprobe instead of ffmpeg.probe
            cmd = [
                'ffprobe', 
                '-v', 'quiet',
                '-print_format', 'json',
                '-show_streams',
                str(input_file)
            ]
            result = subprocess.run(cmd, capture_output=True, text=True)
            if result.returncode != 0:
                raise Exception(f"FFprobe error: {result.stderr}")
            
            probe_data = json.loads(result.stdout)
            video_stream = next((stream for stream in probe_data['streams'] if stream['codec_type'] == 'video'), None)
            
            return ('color_transfer' in video_stream and 'smpte2084' in video_stream['color_transfer'].lower()) or \
                   ('color_primaries' in video_stream and 'bt2020' in video_stream['color_primaries'].lower())
        except Exception as e:
            console.print(f"[yellow]Warning: Could not detect HDR: {str(e)}[/yellow]")
            return False

    def detect_black_bars(self, input_file):
        """Detect letterbox/pillarbox black bars"""
        try:
            console.print("Analyzing video for black bars...")
            ffprobe_command = [
                "ffmpeg", "-hide_banner", "-i", input_file, 
                "-vf", "cropdetect=24:16:0", 
                "-frames:v", "30", "-f", "null", "-"
            ]
            result = subprocess.run(ffprobe_command, 
                                  stderr=subprocess.PIPE, 
                                  stdout=subprocess.DEVNULL,
                                  text=True)
            
            crop_lines = [line for line in result.stderr.split("\n") 
                         if "crop=" in line]
            
            if not crop_lines:
                return None
            
            # Get the most common crop value
            from collections import Counter
            crop_values = [line.split("crop=")[1].split()[0] for line in crop_lines]
            most_common = Counter(crop_values).most_common(1)[0][0]
            
            try:
                w, h, x, y = map(int, most_common.split(":"))
                # Only apply vertical cropping, maintain original width
                probe = ffmpeg.probe(input_file)
                video_stream = next((stream for stream in probe['streams'] if stream['codec_type'] == 'video'), None)
                original_width = int(video_stream['width'])
                return original_width, h, 0, y
            except (ValueError, IndexError):
                return None
            
        except Exception as e:
            console.print(f"[yellow]Warning: Could not detect black bars: {str(e)}[/yellow]")
            return None

    def convert_video(self, input_file, output_file, encoding_preset, crop_values=None):
        """Convert video without HDR conversion"""
        try:
            cmd = [
                'ffmpeg',
                '-i', str(input_file)
            ]
            
            if crop_values:
                w, h, x, y = crop_values
                cmd.extend(['-vf', f'crop={w}:{h}:{x}:{y}'])
            
            cmd.extend(encoding_preset.split())
            cmd.extend(['-c:a', 'aac', '-b:a', '576k'])
            cmd.append(str(output_file))

            ffpb.main(argv=cmd[1:])
            
        except Exception as e:
            raise e

    def calculate_timeline(self, options):
        """Calculate timeline dimensions based on video analysis or manual input"""
        try:
            if options['auto_detect']:
                probe = ffmpeg.probe(options['input_file'])
                video_stream = next((stream for stream in probe['streams'] if stream['codec_type'] == 'video'), None)
                
                original_width = int(video_stream['width'])
                original_height = int(video_stream['height'])
                
                crop_dimensions = self.detect_black_bars(options['input_file'])
                
                console.print("\n[bold blue]===== VIDEO SEQUENCE SETTINGS =====[/bold blue]")
                console.print("[dim]These settings will help you set up your editing timeline correctly[/dim]")
                
                if crop_dimensions:
                    width, height, x, y = crop_dimensions
                    console.print(f"\n[green]Detected crop values: {width}:{height}:{x}:{y}[/green]")
                    console.print("\n[bold white]Open Premiere Pro and follow these steps:[/bold white]")
                    console.print("\n1. File > New > Sequence or Drag & Drop your video into the timeline")
                    console.print("2. Sequence Settings tab")
                    console.print(f"3. Set Resolution to: [bold green]{width} x {height}[/bold green]")
                    console.print("[bold yellow]If you didn't convert to SDR, MAKE SURE TO SDR CONFORM IN SEQUENCE SETTINGS[/bold yellow]")                
                    console.print("5. Click OK")
                else:
                    console.print("\n[bold white]Open Premiere Pro and follow these steps:[/bold white]")
                    console.print("\n1. File > New > Sequence")
                    console.print("2. Set Resolution to: [bold green]{original_width} x {original_height}[/bold green]")
                    console.print("3. Click OK")
            
            input("\nPress Enter to continue...")
            self.clear_screen()
            
        except Exception as e:
            console.print(f"[red]Error calculating dimensions: {str(e)}[/red]")
            input("\nPress Enter to continue...")
            self.clear_screen()

    def search_bluray(self, movie_title):
        console.print(Panel.fit("Searching Blu-ray.com...", title="Status"))
        
        try:
            # Check if input is a direct URL
            if movie_title.startswith('https://www.blu-ray.com'):
                url = movie_title
                details = self.get_movie_details(url)
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
                details = self.get_movie_details(selected_movie['url'])
            
            console.print("\n[bold blue]══ Movie Details ════════[/bold blue]")
            if "Error" in details:
                console.print(f"[red]Error retrieving details: {details['Error']}[/red]")
            else:
                # Extract resolution and aspect ratio from video details
                resolution_match = re.search(r'Resolution:\s*(\d+p)', details["Video"])
                aspect_match = re.search(r'Aspect ratio:\s*(\d+\.?\d*):1', details["Video"])
                
                native_res = resolution_match.group(1) if resolution_match else "Unknown"
                # Use the encoded aspect ratio
                aspect = float(aspect_match.group(1)) if aspect_match else None
                
                # Find closest standard aspect ratio
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

                # Find closest standard aspect ratio
                closest_aspect = min(STANDARD_RESOLUTIONS["4K"].keys(), 
                                   key=lambda x: abs(x - aspect))

                console.print("\n[bold cyan]Source Information:[/bold cyan]")
                console.print(f"[yellow]Native Resolution:[/yellow] {native_res}")
                console.print(f"[yellow]Encoded Aspect Ratio:[/yellow] {aspect:.2f}:1")

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

                console.print("\n[bold yellow]Important Notes:[/bold yellow]")
                console.print("1. Make sure to enable 'HDR Conform' if working with HDR footage")
                
                # Display full technical details
                console.print("\n[bold blue]Full Technical Details[/bold blue]")
                console.print("\n[bold cyan]Video:[/bold cyan]")
                console.print(details["Video"])
                console.print("\n[bold cyan]Audio:[/bold cyan]")
                console.print(details["Audio"])
            
            input("\nPress Enter to continue...")
            self.clear_screen()
            
        except Exception as e:
            console.print(f"[red]Error searching Blu-ray.com: {str(e)}[/red]")
            input("\nPress Enter to continue...")
            self.clear_screen()

    def get_movie_details(self, url):
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
            
            # Extract aspect ratio from video details
            aspect_ratio = None
            if "Video" in details and details["Video"] != "N/A":
                # Update regex to match both "Aspect ratio:" and "Original aspect ratio:" formats
                aspect_match = re.search(r'(?:Original )?[Aa]spect ratio:?\s*(\d+\.?\d*):1', details["Video"])
                if aspect_match:
                    aspect_ratio = float(aspect_match.group(1))
            
            details["AspectRatio"] = aspect_ratio
            return details
            
        except Exception as e:
            return {"Error": str(e)}

    def add_to_path(self, new_path):
        """Add directory to system PATH"""
        import winreg
        with winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, r'SYSTEM\CurrentControlSet\Control\Session Manager\Environment', 0, winreg.KEY_ALL_ACCESS) as key:
            path = winreg.QueryValueEx(key, 'Path')[0]
            if new_path not in path:
                new_path_value = f"{path};{new_path}"
                winreg.SetValueEx(key, 'Path', 0, winreg.REG_EXPAND_SZ, new_path_value)
                os.system('setx PATH "%PATH%"')
                print(f"Added {new_path} to PATH")

    def is_ffmpeg_installed(self):
        """Check if FFmpeg is installed"""
        required_files = ['ffmpeg.exe', 'ffprobe.exe', 'ffplay.exe']
        paths = os.environ["PATH"].split(os.pathsep)
        for path in paths:
            if all(os.path.exists(os.path.join(path, file)) for file in required_files):
                return True
        program_files_path = Path("C:/Program Files/ffmpeg")
        if all((program_files_path / file).exists() for file in required_files):
            return True
        system32_path = Path("C:/Windows/System32")
        if all((system32_path / file).exists() for file in required_files):
            return True
        c_path = Path("C:/ffmpeg")
        if all((c_path / file).exists() for file in required_files):
            return True
        return False

    def is_dmfs_installed(self):
        """Check if DMFS is installed"""
        program_files = Path("C:/Program Files/DebugMode/FrameServer")
        if program_files.exists():
            return True
        return False

    def download_ffmpeg(self, safe_install=True):
        url = "https://github.com/BtbN/FFmpeg-Builds/releases/download/latest/ffmpeg-master-latest-win64-gpl.zip"
        zip_path = "ffmpeg.zip"
        print("Downloading FFmpeg...")
        response = requests.get(url, stream=True)
        total_size = int(response.headers.get('content-length', 0))
        with open(zip_path, 'wb') as f:
            for chunk in response.iter_content(chunk_size=8192):
                if chunk:
                    f.write(chunk)
        print("Download complete. Extracting...")
        required_files = ['ffmpeg.exe', 'ffprobe.exe', 'ffplay.exe']
        if safe_install:
            install_dir = Path("C:/Program Files/ffmpeg")
            install_dir.mkdir(parents=True, exist_ok=True)
            with zipfile.ZipFile(zip_path, 'r') as zip_ref:
                zip_ref.extractall("ffmpeg_temp")
            bin_path = Path("ffmpeg_temp/ffmpeg-master-latest-win64-gpl/bin")
            for file in bin_path.glob('*'):
                if file.name in required_files: 
                    dest = install_dir / file.name
                    if dest.exists():
                        dest.unlink()
                    file.rename(dest)
            self.add_to_path(str(install_dir))
        else:
            with zipfile.ZipFile(zip_path, 'r') as zip_ref:
                zip_ref.extractall("ffmpeg_temp")
            for file in required_files:
                source = f"ffmpeg_temp\\ffmpeg-master-latest-win64-gpl\\bin\\{file}"
                if os.path.exists(source):
                    os.system(f'move "{source}" C:\\Windows\\System32')
        os.system('rmdir /S /Q ffmpeg_temp')
        os.remove(zip_path)

    def install_dokan(self):
        print("\nInstalling Dokan...")
        try:
            dokan_url = "https://github.com/dokan-dev/dokany/releases/download/v1.5.0.3000/Dokan_x64.msi"
            msi_path = "dokan_temp.msi"
            urllib.request.urlretrieve(dokan_url, msi_path)
            install_command = f'msiexec /i "{msi_path}" /qn'
            os.system(install_command)
            os.remove(msi_path)
        except Exception as e:
            print(f"{e}")

    def install_dmfs(self):
        print("\nInstalling DMFS...")
        try:
            # Create directories with explicit error handling
            dmfs_dir = Path("C:/Program Files/DebugMode/FrameServer")
            adobe_dir = Path("C:/Program Files/Adobe/Common/Plug-ins/7.0/MediaCore")
            
            print(f"Creating directory: {dmfs_dir}")
            try:
                dmfs_dir.mkdir(parents=True, exist_ok=True)
            except Exception as e:
                print(f"Error creating DMFS directory: {e}")
                return

            print(f"Creating directory: {adobe_dir}")
            try:
                adobe_dir.mkdir(parents=True, exist_ok=True)
            except Exception as e:
                print(f"Error creating Adobe directory: {e}")
                return

            # Download and install files
            extension_url = "https://github.com/madelyn1337/store/raw/refs/heads/main/dfscPremiereOut.prm"
            zip_url = "https://github.com/madelyn1337/store/raw/refs/heads/main/FrameServer.zip"
            
            # Download and install Adobe extension
            print("Downloading Adobe extension...")
            extension_path = adobe_dir / "dfscPremiereOut.prm"
            try:
                response = requests.get(extension_url)
                response.raise_for_status()  # Raise exception for bad status codes
                with open(extension_path, 'wb') as f:
                    f.write(response.content)
                print(f"Adobe extension installed to: {extension_path}")
            except Exception as e:
                print(f"Error downloading/installing Adobe extension: {e}")
                return

            # Download and extract FrameServer
            print("Downloading FrameServer...")
            try:
                zip_path = "FrameServer.zip"
                response = requests.get(zip_url)
                response.raise_for_status()
                with open(zip_path, 'wb') as f:
                    f.write(response.content)
                
                print("Extracting FrameServer...")
                with zipfile.ZipFile(zip_path, 'r') as zip_ref:
                    zip_ref.extractall(dmfs_dir)
                print(f"FrameServer extracted to: {dmfs_dir}")
                
                # Clean up zip file
                os.remove(zip_path)
                print("Installation completed successfully!")
                
            except Exception as e:
                print(f"Error downloading/extracting FrameServer: {e}")
                if os.path.exists(zip_path):
                    os.remove(zip_path)
                return

        except Exception as e:
            print(f"Error installing DMFS: {e}")
            print("Please try running the script with administrator privileges")

    def open_website(self):
        website_link = "https://scenepacks.com"
        if platform.system() == "Windows":
            os.system(f'start {website_link}')
        elif platform.system() == "Darwin":
            os.system(f'open {website_link}')
        else:
            print(".")

    def check_installations(self):
        """Check installation status of components"""
        self.clear_screen()
        print("\n=== Installation Status ===")
        print(f"FFmpeg: {'Installed ✓' if self.is_ffmpeg_installed() else 'Not Installed ✗'}")
        print(f"DMFS: {'Installed ✓' if self.is_dmfs_installed() else 'Not Installed ✗'}")
        adobe_plugin = Path("C:/Program Files/Adobe/Common/Plug-ins/7.0/MediaCore/dfscPremiereOut.prm")
        print(f"Adobe Plugin: {'Installed ✓' if adobe_plugin.exists() else 'Not Installed ✗'}")
        input("\nPress Enter to continue...")
        self.clear_screen()

    def uninstall_ffmpeg(self):
        import winreg
        print("\nUninstalling FFmpeg...")
        try:
            ffmpeg_dir = Path("C:/Program Files/ffmpeg")
            if ffmpeg_dir.exists():
                os.system('rmdir /S /Q "C:\\Program Files\\ffmpeg"')
            system32_path = Path("C:/Windows/System32/ffmpeg.exe")
            if system32_path.exists():
                os.remove(system32_path)
            c_path = Path("C:/ffmpeg")
            if c_path.exists():
                os.system('rmdir /S /Q "C:\\ffmpeg"')
            with winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, r'SYSTEM\CurrentControlSet\Control\Session Manager\Environment', 0, winreg.KEY_ALL_ACCESS) as key:
                path = winreg.QueryValueEx(key, 'Path')[0]
                new_path = ";".join([p for p in path.split(";") if "ffmpeg" not in p.lower()])
                winreg.SetValueEx(key, 'Path', 0, winreg.REG_EXPAND_SZ, new_path)
                os.system('setx PATH "%PATH%"')
            print("FFmpeg has been uninstalled successfully!")
        except Exception as e:
            print(f"Error uninstalling FFmpeg: {e}")

    def uninstall_dmfs(self):
        print("\nUninstalling DMFS...")
        try:
            dmfs_dir = Path("C:/Program Files/DebugMode/FrameServer")
            if dmfs_dir.exists():
                os.system('rmdir /S /Q "C:\\Program Files\\DebugMode\\FrameServer"')
            adobe_plugin = Path("C:/Program Files/Adobe/Common/Plug-ins/7.0/MediaCore/dfscPremiereOut.prm")
            if adobe_plugin.exists():
                os.remove(adobe_plugin)
        except Exception as e:
            print(f"Error uninstalling DMFS: {e}")        

    def install_media_info(self):
        try:
            if platform.system() == "Windows":
                url = "https://mediaarea.net/download/binary/mediainfo/24.11/MediaInfo_CLI_24.11_Windows_x64.zip"
                temp_dir = os.path.join(os.getenv('TEMP'), "mediainfo_temp")
                os.makedirs(temp_dir, exist_ok=True)
                zip_path = os.path.join(temp_dir, "mediainfo.zip")
                
                print("Downloading MediaInfo...")
                response = requests.get(url)
                with open(zip_path, 'wb') as f:
                    f.write(response.content)
                
                print("Extracting MediaInfo...")
                with zipfile.ZipFile(zip_path, 'r') as zip_ref:
                    zip_ref.extractall(temp_dir)
                
                # Find mediainfo.exe in the extracted contents
                mediainfo_exe = None
                for root, _, files in os.walk(temp_dir):
                    if "mediainfo.exe" in [f.lower() for f in files]:  # Case-insensitive search
                        mediainfo_exe = os.path.join(root, next(f for f in files if f.lower() == "mediainfo.exe"))
                        break
                
                if mediainfo_exe:
                    # Try to install to FFmpeg directory first
                    ffmpeg_dir = Path("C:/Program Files/ffmpeg")
                    if ffmpeg_dir.exists():
                        dest_path = ffmpeg_dir / "mediainfo.exe"
                    else:
                        # Create FFmpeg directory if it doesn't exist
                        ffmpeg_dir.mkdir(parents=True, exist_ok=True)
                        dest_path = ffmpeg_dir / "mediainfo.exe"
                    
                    # Copy the file with elevated privileges
                    try:
                        shutil.copy2(mediainfo_exe, dest_path)
                        print(f"MediaInfo installed successfully to {dest_path}")
                        
                        # Add FFmpeg directory to PATH if not already there
                        self.add_to_path(str(ffmpeg_dir))
                    except PermissionError:
                        print("Error: Insufficient permissions. Please run with administrator privileges.")
                    except Exception as e:
                        print(f"Error copying file: {e}")
                else:
                    print("Error: mediainfo.exe not found in the downloaded package")
                
                # Clean up
                try:
                    shutil.rmtree(temp_dir)
                except Exception as e:
                    print(f"Warning: Could not clean up temporary files: {e}")
                
        except Exception as e:
            print(f"Error installing MediaInfo: {e}")
            print("Please try running the script with administrator privileges")

    def installers_menu(self):
        """Handle installer and uninstaller options"""
        while True:
            self.clear_screen()
            questions = [
                inquirer.List('choice',
                    message='Select an option:',
                    choices=[
                        'Install All',
                        'Uninstall All',
                        'Check Installations',
                        'Back to Main Menu'
                    ]
                )
            ]
            
            answer = inquirer.prompt(questions)
            
            if answer['choice'] == 'Install All':
                self.download_ffmpeg()
                self.install_dokan()
                self.install_dmfs()
                self.install_media_info()
            elif answer['choice'] == 'Uninstall All':
                self.uninstall_ffmpeg()
                self.uninstall_dmfs()
            elif answer['choice'] == 'Check Installations':
                self.check_installations()
            else:
                return


    def set_preset(self):
        try:
            self.clear_screen()
            
            # Get input source file
            questions = [
                inquirer.Text(
                    'input_file',
                    message='Drag & drop source video file (or enter path)',
                    validate=lambda _, x: Path(self.strip_quotes(x)).exists()
                ),
                inquirer.Confirm(
                    'auto_crop',
                    message='Enable automatic black bar detection?',
                    default=True
                ),
                inquirer.Confirm(
                    'tonemap',
                    message='Enable HDR to SDR conversion?',
                    default=False
                )
            ]
            
            answers = inquirer.prompt(questions)
            if not answers:
                return
            
            # Clean up input path
            input_file = Path(self.strip_quotes(answers['input_file'])).resolve()

            # Get output filename (removed validation since we're creating a new file)
            name_question = [
                inquirer.Text('output_name',
                    message='Enter output filename (without extension)'
                )
            ]
            
            name_answer = inquirer.prompt(name_question)
            if not name_answer:
                return
            
            # Preset selection
            preset_question = [
                inquirer.List('preset',
                    message='Select encoding preset:',
                    choices=[
                        '411 Clarity Pro (For High Bitrate)',
                        '411 Stream (Web Optimized)',
                        '411 Grain Pro (For High Bitrate)',
                        '411 Grain Stream (Web Optimized)',
                        'Custom Encode (Admin Only)'
                    ]
                )
            ]
            
            preset_answer = inquirer.prompt(preset_question)
            if not preset_answer:
                return
            
            # Define preset parameters
            presets = {
                '411 Clarity Pro (For High Bitrate)': '-c:v libx265 -preset medium -crf 18 -x265-params profile=main10',
                '411 Stream (Web Optimized)': '-c:v libx265 -preset medium -crf 20 -x265-params profile=main10',
                '411 Grain Pro (For High Bitrate)': '-c:v libx265 -preset medium -crf 16 -x265-params profile=main10:grain=8',
                '411 Grain Stream (Web Optimized)': '-c:v libx265 -preset medium -crf 18 -x265-params profile=main10:grain=6'
            }

            # Handle custom preset
            if preset_answer['preset'] == 'Custom Encode (Admin Only)':
                password = inquirer.Password('password',
                    message='Enter admin password'
                ).execute()
                
                if password != '114':
                    console.print("[red]Invalid password![/red]")
                    input("\nPress Enter to continue...")
                    return
                
                encoding_params = inquirer.Text('command',
                    message='Enter custom FFmpeg parameters'
                ).execute()
            else:
                encoding_params = presets[preset_answer['preset']]

            # Get CPU thread count
            cpu_threads = psutil.cpu_count(logical=False)
            
            # Build the base FFmpeg command
            ffmpeg_base = f'ffmpeg -i "$_" -threads {cpu_threads} '
            
            # Initialize filter string
            filters = []
            
            # Add crop if requested
            if answers['auto_crop']:
                crop_values = self.detect_black_bars(input_file)
                if crop_values:
                    w, h, x, y = crop_values
                    filters.append(f'crop={w}:{h}:{x}:{y}')
            
            # Add tonemapping if requested
            if answers['tonemap']:
                tonemap_filter = 'zscale=t=linear:npl=203,format=gbrpf32le,tonemap=reinhard:desat=0,zscale=p=709:t=709:m=709:r=limited:dither=error_diffusion,format=yuv420p,sidedata=delete'
                filters.append(tonemap_filter)
            
            # Add filters to command if any exist
            if filters:
                ffmpeg_base += f'-vf "{",".join(filters)}" '
            
            # Add audio processing
            ffmpeg_base += '-c:a aac -b:a 576k '
            
            # Add encoding parameters
            ffmpeg_base += f'{encoding_params} '
            
            # Setup output path
            scenepacks_dir = self.base_dir / 'scenepacks'
            scenepacks_dir.mkdir(exist_ok=True)
            output_path = scenepacks_dir / f"{name_answer['output_name']}.mp4"
            
            # Create complete PowerShell command
            ffmpeg_command = f'powershell.exe -c "Get-ChildItem \\"C:\\DMFS\\virtual\\*.avi\\" | ForEach-Object {{ {ffmpeg_base} \\"\\"\\"{output_path}\\"\\"\\" }}"'
            
            # Set registry values
            ps_script = f'''
            Set-ItemProperty -Path "HKCU:\\Software\\DebugMode\\FrameServer" -Name "runCommandOnFsStart" -Value 1 -Type DWord
            Set-ItemProperty -Path "HKCU:\\Software\\DebugMode\\FrameServer" -Name "endAfterRunningCommand" -Value 1 -Type DWord
            Set-ItemProperty -Path "HKCU:\\Software\\DebugMode\\FrameServer" -Name "pcmAudioInAvi" -Value 1 -Type DWord
            Set-ItemProperty -Path "HKCU:\\Software\\DebugMode\\FrameServer" -Name "commandToRunOnFsStart" -Value '{ffmpeg_command}'
            '''
            
            result = subprocess.run(['powershell', '-Command', ps_script], capture_output=True, text=True)
            
            if result.returncode != 0:
                raise Exception(f"PowerShell Error: {result.stderr}")
            
            console.print("[green]Preset configured successfully![/green]")
            
        except Exception as e:
            console.print(f"[red]Error setting preset: {str(e)}[/red]")
        
        input("\nPress Enter to continue...")

    def edl_conform_menu(self):
        """Convert Premiere EDL to FFmpeg commands for segment extraction"""
        while True:
            self.clear_screen()
            
            # Create EDL Export directory
            edl_export_dir = self.base_dir / 'EDL Export'
            edl_export_dir.mkdir(exist_ok=True)
            
            # Get input EDL file - Modified to handle drag & drop
            file_question = [
                inquirer.Text(
                    'edl_file',
                    message='Drag & drop EDL file (or enter path)',
                    validate=lambda _, x: Path(self.strip_quotes(x)).exists()
                )
            ]
            
            file_answer = inquirer.prompt(file_question)
            if not file_answer:
                return
            
            # Clean up EDL path
            edl_file = Path(self.strip_quotes(file_answer['edl_file']))
            
            # Get source video file - Modified to handle drag & drop
            source_question = [
                inquirer.Text(
                    'source_file',
                    message='Drag & drop source video file (or enter path)',
                    validate=lambda _, x: Path(self.strip_quotes(x)).exists()
                )
            ]
            source_answer = inquirer.prompt(source_question)
            if not source_answer:
                return
            
            if platform.system() == "Windows":

                source_file = Path(self.strip_quotes(source_answer['source_file'])).resolve()
            else:
                source_file = Path(self.strip_quotes(source_answer['source_file'])).resolve()
            
            # Get output name
            name_question = [
                inquirer.Text(
                    'output_name',
                    message='Enter final output filename (without extension)',
                    validate=lambda _, x: Path(self.strip_quotes(x)).exists(),
                )
            ]
            
            name_answer = inquirer.prompt(name_question)
            if not name_answer:
                return
            
            try:
                # Analyze source frame rate and get GOP size
                probe = ffmpeg.probe(str(source_file))
                video_stream = next(
                    (stream for stream in probe['streams'] if stream['codec_type'] == 'video'), None
                )
                
                if not video_stream:
                    raise ValueError("No video stream found in source file.")
                    
                # Get exact frame rate
                if 'r_frame_rate' in video_stream:  
                    num, den = map(int, video_stream['r_frame_rate'].split('/'))
                    frame_rate = num / den if den != 0 else None
                else:
                    num, den = map(int, video_stream['avg_frame_rate'].split('/'))
                    frame_rate = num / den if den != 0 else None

                if not frame_rate:
                    raise ValueError("Unable to detect frame rate from the source video file.")

                console.print(f"[cyan]Detected source frame rate: {frame_rate:.3f} fps[/cyan]")

                # Parse EDL file
                console.print("\n[cyan]Parsing EDL file...[/cyan]")
                segments = []

                def is_valid_timecode(tc):
                    """Validate timecode format"""
                    parts = tc.split(':')
                    return len(parts) == 4 and all(part.isdigit() for part in parts)

                with open(edl_file, 'r', encoding='utf-8') as f:
                    lines = f.readlines()

                    for line in lines:
                        line = line.strip()
                        if not line or line.startswith('*') or 'AUDIO' in line:
                            continue

                        if line[0].isdigit():
                            parts = line.split()
                            if len(parts) >= 7:
                                source_in_tc = parts[4]
                                source_out_tc = parts[5]

                                if is_valid_timecode(source_in_tc) and is_valid_timecode(source_out_tc):
                                    source_in = self.timecode_to_seconds(source_in_tc, frame_rate)
                                    source_out = self.timecode_to_seconds(source_out_tc, frame_rate)

                                    if source_in is not None and source_out is not None:
                                        segments.append({'in': source_in, 'out': source_out})
                                        console.print(
                                            f"[dim]Found segment: {source_in_tc} to {source_out_tc}[/dim]"
                                        )
                                else:
                                    console.print(f"[yellow]Invalid timecodes in line: {line}[/yellow]")

                if not segments:
                    raise Exception("No valid segments found in EDL file")

                console.print(f"\n[cyan]Found {len(segments)} valid segments[/cyan]")

                # Extract each segment using FFmpeg with improved accuracy
                for i, segment in enumerate(segments):
                    output_segment = edl_export_dir / f"temp_segment_{i:03d}.mp4"
                    
                    # Calculate frame-accurate timestamps
                    start_frame = int(segment['in'] * frame_rate)
                    end_frame = int(segment['out'] * frame_rate)
                    
                    # Convert back to seconds for precise cutting
                    start_time = start_frame / frame_rate
                    duration = (end_frame - start_frame) / frame_rate
                    
                    cmd = [
                        'ffmpeg',
                        '-hide_banner',
                        '-ss', f"{start_time:.6f}",  # Increased precision
                        '-i', str(source_file),
                        '-map', '0',  # Copy all streams
                        '-avoid_negative_ts', '1',
                        '-async', '1',  # Audio sync
                        '-strict', '-2',
                        '-t', f"{duration:.6f}",
                        '-c', 'copy',  # Use stream copy for speed
                        str(output_segment)
                    ]

                    console.print(
                        f"Processing segment {i+1}/{len(segments)}: "
                        f"Frame {start_frame} to {end_frame} "
                        f"(Duration: {duration:.3f}s)"
                    )
                    
                    result = subprocess.run(cmd, capture_output=True, text=True)
                    if result.returncode != 0:
                        console.print(
                            f"[red]Error processing segment {i+1}: {result.stderr}[/red]"
                        )

                console.print(f"\n[green]Successfully processed {len(segments)} segments[/green]")

                # After all segments are processed, create concat file
                concat_file = edl_export_dir / 'concat.txt'
                with open(concat_file, 'w', encoding='utf-8') as f:
                    for i in range(len(segments)):
                        segment_path = edl_export_dir / f"temp_segment_{i:03d}.mp4"
                        f.write(f"file '{segment_path.name}'\n")

                # Create final output file
                final_output = edl_export_dir / f"{name_answer['output_name']}.mp4"
                
                console.print("\n[cyan]Combining segments into final video...[/cyan]")
                
                mux_cmd = [
                    'ffmpeg',
                    '-f', 'concat',
                    '-safe', '0',
                    '-i', str(concat_file),
                    '-c', 'copy',
                    str(final_output)
                ]
                
                result = subprocess.run(mux_cmd, capture_output=True, text=True)
                if result.returncode != 0:
                    raise Exception(f"Error during final mux: {result.stderr}")

                # Clean up intermediate files
                console.print("\n[cyan]Cleaning up temporary files...[/cyan]")
                for i in range(len(segments)):
                    segment_path = edl_export_dir / f"temp_segment_{i:03d}.mp4"
                    try:
                        segment_path.unlink()
                    except Exception as e:
                        console.print(f"[yellow]Warning: Could not delete {segment_path.name}: {e}[/yellow]")
                
                # Delete concat file
                try:
                    concat_file.unlink()
                except Exception as e:
                    console.print(f"[yellow]Warning: Could not delete concat file: {e}[/yellow]")

                console.print(f"\n[green]Successfully created final video: {final_output.name}[/green]")
                console.print(f"[dim]Location: {final_output}[/dim]")

                # After successful EDL export, ask about proxy
                proxy_question = [
                    inquirer.Confirm('create_proxy',
                        message='Would you like to create an H.264 proxy?',
                        default=True
                    )
                ]
                
                proxy_answer = inquirer.prompt(proxy_question)
                if proxy_answer and proxy_answer['create_proxy']:
                    final_output = edl_export_dir / f"{name_answer['output_name']}.mp4"
                    proxy_output = self.base_dir / 'proxies' / f"{name_answer['output_name']}_proxy.mp4"
                    
                    ffmpeg_cmd = (
                        f'ffpb -i "{final_output}" '
                        f'-c:v libx264 -preset fast -crf 23 '
                        f'-c:a aac -b:a 576k '
                        f'"{proxy_output}"'
                    )
                    
                    # Launch new terminal window based on OS
                    if platform.system() == "Windows":
                        subprocess.Popen(['start', 'cmd', '/k', ffmpeg_cmd], shell=True)
                    else:  # macOS
                        apple_script = (
                            f'tell application "Terminal" to do script "{ffmpeg_cmd}"'
                        )
                        subprocess.run(['osascript', '-e', apple_script])

            except Exception as e:
                console.print(f"[red]Error: {str(e)}[/red]")

            input("\nPress Enter to continue...")
            self.clear_screen()
            return

    def timecode_to_seconds(self, timecode, frame_rate):
        """Convert timecode (HH:MM:SS:FF) to seconds with source-aware frame rate"""
        try:
            hours, minutes, seconds, frames = map(int, timecode.split(':'))
            total_seconds = (hours * 3600) + (minutes * 60) + seconds + (frames / frame_rate)
            return round(total_seconds, 6)  # Higher precision for accurate cuts
        except Exception as e:
            console.print(f"[yellow]Warning: Timecode conversion error: {str(e)}[/yellow]")
            return 0

    def is_valid_timecode(self, tc):
        """Validate timecode format"""
        try:
            parts = tc.split(':')
            return len(parts) == 4 and all(part.isdigit() for part in parts)
        except:
            return False

def is_admin():
    """Check if the script is running with admin privileges"""
    try:
        if platform.system() == "Windows":
            return ctypes.windll.shell32.IsUserAnAdmin()
        else:
            return os.geteuid() == 0
    except:
        return False

def run_as_admin():
    if not is_admin():
        if platform.system() == "Windows":
            script = os.path.abspath(sys.argv[0])
            params = ' '.join(sys.argv[1:])
            ret = ctypes.windll.shell32.ShellExecuteW(None, "runas", sys.executable, f'"{script}" {params}', None, 1)
            if ret <= 32:
                raise Exception("Failed to elevate privileges")
            sys.exit(0)
        else:
            os.execvp('sudo', ['sudo', 'python3'] + sys.argv)
            sys.exit()

def main():
    try:
        # Check if running with command line arguments
        if len(sys.argv) > 1:
            processor = VideoProcessor()
            if sys.argv[1] == "preset_continue":
                if not is_admin():
                    print("Error: Continuation requires admin privileges")
                    sys.exit(1)
                processor._continue_preset_setup()
                sys.exit(0)
            elif sys.argv[1] in ["1"]:  # Handle numeric choices for installers
                choice = sys.argv[1]
                if choice == "1":
                    processor.clear_screen()
                    processor.installers_menu()
            elif sys.argv[1] == '-installers':
                processor.installers_menu()
            sys.exit(0)

        # Normal menu flow
        processor = VideoProcessor()
        processor.display_main_menu()
    except KeyboardInterrupt:
        print("\n")  # Add a newline for cleaner exit
        sys.exit(0)
    except Exception as e:
        console.print(f"\nAn error occurred: {str(e)}", style="bold red")
        sys.exit(1)

if __name__ == "__main__":
    main()

