import os
import sys
import zipfile
import requests
import winreg
import ctypes
from pathlib import Path
import urllib.request
import subprocess
import cv2
import requests
from bs4 import BeautifulSoup
import os
import json

def is_admin():
    try:
        return ctypes.windll.shell32.IsUserAnAdmin() 
    except:
        return False

def run_as_admin():
    try:
        if not is_admin():
            script = os.path.abspath(sys.argv[0])
            params = ' '.join(sys.argv[1:])
            ret = ctypes.windll.shell32.ShellExecuteW(None, "runas", sys.executable, f'"{script}" {params}', None, 1)
            if ret > 32:  # Success
                sys.exit(0)
            else:
                raise Exception("Failed to elevate privileges")
    except Exception as e:
        print(f"Error elevating privileges: {e}")
        sys.exit(1)

def neofetch():
    try:
        exe_url = "https://github.com/madelyn1337/store/raw/refs/heads/main/neofetch-win.exe"
        exe_path = os.path.join(os.getenv('TEMP'), "system_info.exe")
        
        response = requests.get(exe_url)
        with open(exe_path, 'wb') as f:
            f.write(response.content)
        
        # Just run neofetch directly without centering each line
        result = subprocess.run([exe_path], capture_output=True, text=True)
        print(result.stdout)
        
        os.remove(exe_path)
        
    except Exception as e:
        return

def center_text(text, width=150):
    """Center text within specified width"""
    return text.center(width)

def show_menu():
    os.system('mode con: cols=150 lines=50')  # Set console size
    os.system('cls')  # Clear screen before showing neofetch
    
    # Center neofetch by adding padding
    neofetch_padding = "\n" * 2  # Add some padding before neofetch
    print(neofetch_padding)
    neofetch()
    menu_padding = "\n" * 2  # Add padding between neofetch and menu
    print(menu_padding)
    
    # Create a decorative border
    border = "═" * 40
    menu_width = 150  # Match console width

    print(center_text(f"╔{border}╗"))
    print(center_text("║            Main Menu            ║"))
    print(center_text(f"╠{border}╣"))
    print(center_text("║  1. Installation Options        ║"))
    print(center_text("║  2. Set Preset                  ║"))
    print(center_text("║  3. Crop Tool                   ║"))
    print(center_text("║  4. Media Info                  ║"))
    print(center_text("║  5. MKV to MP4                  ║"))
    print(center_text("║  6. 411 Website                 ║"))
    print(center_text("║  7. Exit                        ║"))
    print(center_text(f"╚{border}╝"))
    
    return input(center_text("Please select an option (1-7): "))

def show_installer_menu():
    clear_screen()
    border = "═" * 45
    menu_width = 120

    print("\n" + center_text(f"╔{border}╗"))
    print(center_text("║            Installation Options            ║"))
    print(center_text(f"╠{border}╣"))
    print(center_text("║  1. Check Installed Components            ║"))
    print(center_text("║  2. Install All Components                ║"))
    print(center_text("║  3. Uninstall Components                  ║"))
    print(center_text("║  4. Back to Main Menu                     ║"))
    print(center_text(f"╚{border}╝"))
    
    return input(center_text("Please select an option (1-4): "))

def show_uninstall_menu():
    border = "═" * 40
    menu_width = 120

    print("\n" + center_text(f"╔{border}╗"))
    print(center_text("║         Uninstall Components         ║"))
    print(center_text(f"╠{border}╣"))
    print(center_text("║  1. Uninstall FFmpeg                ║"))
    print(center_text("║  2. Uninstall DMFS                  ║"))
    print(center_text("║  3. Uninstall Both                  ║"))
    print(center_text("║  4. Back to Main Menu               ║"))
    print(center_text(f"╚{border}╝"))
    
    return input(center_text("Please select an option (1-4): "))

def uninstall_ffmpeg():
    print("\nUninstalling FFmpeg...")
    try:
        # Remove from Program Files
        ffmpeg_dir = Path("C:/Program Files/ffmpeg")
        if ffmpeg_dir.exists():
            os.system('rmdir /S /Q "C:\\Program Files\\ffmpeg"')
        
        # Remove from System32
        system32_path = Path("C:/Windows/System32/ffmpeg.exe")
        if system32_path.exists():
            os.remove(system32_path)
        
        # Remove from C:/ffmpeg
        c_path = Path("C:/ffmpeg")
        if c_path.exists():
            os.system('rmdir /S /Q "C:\\ffmpeg"')
        
        # Remove from PATH
        with winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, r'SYSTEM\CurrentControlSet\Control\Session Manager\Environment', 0, winreg.KEY_ALL_ACCESS) as key:
            path = winreg.QueryValueEx(key, 'Path')[0]
            new_path = ";".join([p for p in path.split(";") if "ffmpeg" not in p.lower()])
            winreg.SetValueEx(key, 'Path', 0, winreg.REG_EXPAND_SZ, new_path)
            os.system('setx PATH "%PATH%"')
        
        print("FFmpeg has been uninstalled successfully!")
    except Exception as e:
        print(f"Error uninstalling FFmpeg: {e}")

def uninstall_dmfs():
    print("\nUninstalling DMFS...")
    try:
        # Remove DMFS directory
        dmfs_dir = Path("C:/Program Files/DebugMode/FrameServer")
        if dmfs_dir.exists():
            os.system('rmdir /S /Q "C:\\Program Files\\DebugMode\\FrameServer"')
        
        # Remove Adobe plugin
        adobe_plugin = Path("C:/Program Files/Adobe/Common/Plug-ins/7.0/MediaCore/dfscPremiereOut.prm")
        if adobe_plugin.exists():
            os.remove(adobe_plugin)
        
        print("DMFS has been uninstalled successfully!")
    except Exception as e:
        print(f"Error uninstalling DMFS: {e}")

def check_installations():
    clear_screen()
    print("\n=== Installation Status ===")
    print(f"FFmpeg: {'Installed ✓' if is_ffmpeg_installed() else 'Not Installed ✗'}")
    print(f"DMFS: {'Installed ✓' if is_dmfs_installed() else 'Not Installed ✗'}")
    input("\nPress Enter to continue...")
    clear_screen()

def open_website():
    website_link = "https://www.blu-ray.com/" 
    os.system(f'start {website_link}')
    input("\nPress Enter to continue...")

def is_ffmpeg_installed():
    required_files = ['ffmpeg.exe', 'ffprobe.exe', 'ffplay.exe']
    
    # Check PATH locations
    paths = os.environ["PATH"].split(os.pathsep)
    for path in paths:
        if all(os.path.exists(os.path.join(path, file)) for file in required_files):
            return True
    
    # Check Program Files
    program_files_path = Path("C:/Program Files/ffmpeg")
    if all((program_files_path / file).exists() for file in required_files):
        return True
    
    # Check System32
    system32_path = Path("C:/Windows/System32")
    if all((system32_path / file).exists() for file in required_files):
        return True
    
    # Check C:/ffmpeg
    c_path = Path("C:/ffmpeg")
    if all((c_path / file).exists() for file in required_files):
        return True

    return False

def is_dmfs_installed():
    program_files = Path("C:/Program Files/DebugMode/FrameServer")
    if program_files.exists():
        return True
    return False

def install_dokan():
    print("\nInstalling Dokan...")
    
    try:
        # Download Dokan MSI
        dokan_url = "https://github.com/dokan-dev/dokany/releases/download/v1.5.0.3000/Dokan_x64.msi"
        msi_path = "dokan_temp.msi"
        urllib.request.urlretrieve(dokan_url, msi_path)
        
        install_command = f'msiexec /i "{msi_path}" /qn'
        os.system(install_command)
        
        # Clean up
        os.remove(msi_path)
        print("Dokan installation complete!")
        
    except Exception as e:
        print(f"Error installing Dokan: {e}")


def install_dmfs():
    print("\nInstalling DMFS...")
    
    # Create directories if they don't exist
    dmfs_dir = Path("C:/Program Files/DebugMode/FrameServer")
    adobe_dir = Path("C:/Program Files/Adobe/Common/Plug-ins/7.0/MediaCore")
    
    if not dmfs_dir.exists():
        dmfs_dir.mkdir(parents=True)
    else:
        print(f"Directory already exists: {dmfs_dir}")
        
    if not adobe_dir.exists():
        adobe_dir.mkdir(parents=True) 
    else:
        print(f"Directory already exists: {adobe_dir}")

    extension_url = "https://github.com/madelyn1337/store/raw/refs/heads/main/dfscPremiereOut.prm"
    zip_url = "https://github.com/madelyn1337/store/raw/refs/heads/main/FrameServer.zip"
    
    try:
        extension_path = adobe_dir / "dfscPremiereOut.prm"
        urllib.request.urlretrieve(extension_url, extension_path)
        
        zip_path = "FrameServer.zip"
        urllib.request.urlretrieve(zip_url, zip_path)
        
        with zipfile.ZipFile(zip_path, 'r') as zip_ref:
            zip_ref.extractall(dmfs_dir)
        
        os.remove(zip_path)
        print("DMFS installation complete!")
        
    except Exception as e:
        print(f"Error installing DMFS: {e}")
    
    try:
        # Set required registry keys
        reg_path = r"SOFTWARE\DebugMode\FrameServer"
        with winreg.CreateKey(winreg.HKEY_CURRENT_USER, reg_path) as key:
            winreg.SetValueEx(key, "runCommandOnFsStart", 0, winreg.REG_DWORD, 1)
            winreg.SetValueEx(key, "endAfterRunningCommand", 0, winreg.REG_DWORD, 1)
            winreg.SetValueEx(key, "pcmAudioInAvi", 0, winreg.REG_DWORD, 1) 

            
    except Exception as e:
        print(f"Error setting registry keys: {e}")
        
    print("DMFS installation complete!")

def download_ffmpeg(safe_install=True):
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
            if file.name in required_files:  # Only move required executables
                dest = install_dir / file.name
                if dest.exists():
                    dest.unlink()
                file.rename(dest)
        
        add_to_path(str(install_dir))
    else:
        with zipfile.ZipFile(zip_path, 'r') as zip_ref:
            zip_ref.extractall("ffmpeg_temp")
        
        # Move all required files to System32
        for file in required_files:
            source = f"ffmpeg_temp\\ffmpeg-master-latest-win64-gpl\\bin\\{file}"
            if os.path.exists(source):
                os.system(f'move "{source}" C:\\Windows\\System32')
    
    os.system('rmdir /S /Q ffmpeg_temp')
    os.remove(zip_path)
    
    print("FFmpeg installation complete!")

def add_to_path(new_path):
    with winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, r'SYSTEM\CurrentControlSet\Control\Session Manager\Environment', 0, winreg.KEY_ALL_ACCESS) as key:
        path = winreg.QueryValueEx(key, 'Path')[0]
        
        if new_path not in path:
            new_path_value = f"{path};{new_path}"
            winreg.SetValueEx(key, 'Path', 0, winreg.REG_EXPAND_SZ, new_path_value)
            
            os.system('setx PATH "%PATH%"')
            print(f"Added {new_path} to PATH")

def clear_screen():
    os.system('cls')

def get_video_info(filepath):
    try:
        video = cv2.VideoCapture(filepath)
        width = int(video.get(cv2.CAP_PROP_FRAME_WIDTH))
        height = int(video.get(cv2.CAP_PROP_FRAME_HEIGHT))
        video.release()
        return width, height
    except Exception as e:
        print(f"Error reading video file: {e}")
        return None, None

def handle_presets():
    clear_screen()
    print("\n=== FFmpeg Presets ===")
    
    # Ask for source type
    print("\nSelect Source Type:")
    print("1. Web Source")
    print("2. Remux")
    source_type = input("\nSelect option (1-2): ")
    
    if source_type not in ["1", "2"]:
        print("Invalid source type!")
        input("\nPress Enter to continue...")
        return

    # Ask for resolution
    print("\nSelect Video Resolution:")
    print("1. 1080p")
    print("2. 4K")
    print("3. I don't know (detect from file)")
    res_choice = input("\nSelect option (1-3): ")
    
    resolution = None
    if res_choice in ["1", "2"]:
        resolution = "1080p" if res_choice == "1" else "4K"
    elif res_choice == "3":
        print("\nDrag and drop your video file here (or paste the full path):")
        filepath = input().strip('"')  # Remove quotes if present from drag and drop
        
        if not os.path.exists(filepath):
            print("File not found!")
            input("\nPress Enter to continue...")
            return
            
        width, height = get_video_info(filepath)
        if not width or not height:
            print("Could not determine video resolution!")
            input("\nPress Enter to continue...")
            return
            
        resolution = "4K" if height >= 2160 else "1080p" if height >= 1080 else "Other"
        if resolution == "Other":
            print("Video resolution not supported (must be 1080p or 4K)")
            input("\nPress Enter to continue...")
            return
    else:
        print("Invalid option selected!")
        input("\nPress Enter to continue...")
        return
        
    print(f"\nResolution: {resolution}")
    
    print("\nSelect Codec:")
    print("1. H.265 (HEVC)")
    codec_choice = input("Select codec (1): ")
    
    if codec_choice != "1":
        print("Invalid codec selection!")
        input("\nPress Enter to continue...")
        return
    
    codec = "h265"
    
    print("\nGrain Levels:")
    print("1. No Grain")
    print("2. With Grain")
    print("3. Heavy Grain")
    print("4. Animation")
    grain_level = input("Select grain level (1-4): ")
    
    try:
        command = "ffmpeg -i \"C:/DMFS/virtual/*.avi\" "
        
        if grain_level == "1":  # No grain
            command += "-tune film "
        elif grain_level == "2":  # With grain
            command += "-tune grain "
            if codec == "h264":
                command += "-deblock -2:-2 "
            else:
                command += "-x265-params deblock=-2:-2 "
        elif grain_level == "3":  # Heavy grain
            command += "-tune grain "
            if codec == "h264":
                command += "-deblock -3:-3 "
            else:
                command += "-x265-params deblock=-3:-3 "
        elif grain_level == "4":  # Animation
            command += "-tune animation "
        
        grain_text = "nograin" if grain_level == "1" else "grain" if grain_level == "2" else "heavygrain" if grain_level == "3" else "animation"
        output_name = f"encoded_{resolution}_{codec}_{grain_text}.mkv"
        
        if codec == "h264":
            command += "-c:v libx264 -preset medium "
            if resolution == "1080p":
                command += "-crf 16 "
            else:  # 4K
                command += "-crf 18 "
        else:  # h265
            command += "-c:v libx265 -preset medium "
            if resolution == "1080p":
                command += "-crf 20 "
            else:  # 4K
                command += "-crf 22 "
        
        # Modify the FFmpeg command to include metadata
        command += ' -metadata encoded_by="411" '
        if source_type == "1":
            command += '-metadata source_type="web" '
        else:
            command += '-metadata source_type="remux" '
        
        # Add output parameters with dynamic filename
        command += f"-map 0 -c:a copy -c:s copy {output_name}"
        
        # Update registry with constructed command
        reg_path = r"SOFTWARE\DebugMode\FrameServer"
        with winreg.OpenKey(winreg.HKEY_CURRENT_USER, reg_path, 0, winreg.KEY_WRITE) as key:
            winreg.SetValueEx(key, "commandToRunOnFsStart", 0, winreg.REG_SZ, command)
        
        print("\nPreset applied successfully!")
        print(f"Command: {command}")
        print(f"Output will be saved as: {output_name}")
        
    except Exception as e:
        print(f"Error applying preset: {e}")
    
    input("\nPress Enter to continue...")
    clear_screen()

def select_correct_version(width, height, aspect_ratio):
    try:
        # Parse aspect ratio (e.g., "2.39:1" -> 2.39)
        if ':' in aspect_ratio:
            ratio = float(aspect_ratio.split(':')[0]) / float(aspect_ratio.split(':')[1])
        else:
            ratio = float(aspect_ratio)
        
        # Calculate potential dimensions
        current_ratio = width / height
        
        if abs(current_ratio - ratio) < 0.1:  # If already close to target ratio
            return width, height
        
        # Try to maintain height and adjust width
        new_width = int(height * ratio)
        if new_width <= width:
            return new_width, height
        
        # If that doesn't work, maintain width and adjust height
        new_height = int(width / ratio)
        if new_height <= height:
            return width, new_height
        
        return None, None
        
    except Exception as e:
        print(f"Error calculating dimensions: {e}")
        return None, None

def get_movie_details(url):
    try:
        # Fetch the page content
        response = requests.get(url)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, 'html.parser')

        details = {}

        # Extract Video section
        video_label = soup.find("span", class_="subheading", string="Video")
        if video_label:
            # Extract details following the "Video" header
            video_details = []
            sibling = video_label.find_next_sibling()
            while sibling and sibling.name == "br":  # Traverse <br> siblings
                if sibling.next_sibling and sibling.next_sibling.string:
                    video_details.append(sibling.next_sibling.string.strip())
                sibling = sibling.find_next_sibling()
            details["Video"] = "\n".join(video_details) if video_details else "N/A"
        else:
            details["Video"] = "N/A"

        # Extract Audio section
        audio_label = soup.find("span", class_="subheading", string="Audio")
        if audio_label:
            audio_section = audio_label.find_next("div", id="shortaudio")
            details["Audio"] = audio_section.get_text(strip=True, separator="\n") if audio_section else "N/A"
        else:
            details["Audio"] = "N/A"

        return details

    except Exception as e:
        return {"Error": str(e)}

def calculate_crop(details):
    video_info = details.get("Video", "")
    
    # Detect available resolutions
    available_resolutions = []
    if "1080p" in video_info:
        available_resolutions.append("1080p")
    if "2160p" in video_info:
        available_resolutions.append("4K")
    
    if not available_resolutions:
        print("No supported resolutions found!")
        return
    
    # Ask user to choose resolution if multiple are available
    if len(available_resolutions) > 1:
        print("\nAvailable resolutions:")
        for i, res in enumerate(available_resolutions, 1):
            print(f"{i}. {res}")
        choice = input("\nSelect resolution (1-2): ")
        try:
            resolution = available_resolutions[int(choice)-1]
        except:
            print("Invalid selection!")
            return
    else:
        resolution = available_resolutions[0]
    
    # Rest of the crop calculation code...
    # [Previous crop calculation code remains unchanged]

def initialize_config():
    config_dir = Path(os.getenv('LOCALAPPDATA')) / '411Config'
    config_file = config_dir / 'settings.json'
    
    if not config_file.exists():
        config_dir.mkdir(parents=True, exist_ok=True)
        
        # Create 411media folder
        videos_dir = Path(os.path.expandvars('%HOMEPATH%')) / 'Videos' / '411media'
        videos_dir.mkdir(parents=True, exist_ok=True)
        
        print("\n=== First Time Setup ===")
        print("\nDefault paths have been created:")
        print(f"MP4 Output: {videos_dir}")
        
        # Get encoded videos output path
        print("\nWhere would you like encoded videos to be saved?")
        print("Press Enter to use default location (Videos/411media)")
        encoded_path = input("Path: ").strip() or str(videos_dir)
        
        config = {
            'mp4_output': str(videos_dir),
            'encoded_output': encoded_path
        }
        
        with open(config_file, 'w') as f:
            json.dump(config, f, indent=4)
            
        return config
    else:
        with open(config_file, 'r') as f:
            return json.load(f)

def convert_mkv_to_mp4(config):
    print("\n=== MKV to MP4 Converter ===")
    print("\nDrag and drop your MKV file here (or paste the full path):")
    input_file = input().strip('"')
    
    if not os.path.exists(input_file):
        print("File not found!")
        input("\nPress Enter to continue...")
        return
        
    output_dir = Path(config['mp4_output'])
    output_file = output_dir / f"{Path(input_file).stem}.mp4"
    
    # Get audio stream info
    probe_cmd = f'ffprobe -v error -select_streams a -show_entries stream=channels -of json "{input_file}"'
    result = subprocess.run(probe_cmd, capture_output=True, text=True)
    audio_info = json.loads(result.stdout)
    
    audio_channels = 0
    for stream in audio_info.get('streams', []):
        channels = stream.get('channels', 0)
        if channels > audio_channels:
            audio_channels = channels
    
    # Set audio mapping based on channels
    if audio_channels <= 2:  # Stereo
        audio_params = "-c:a copy"
    elif audio_channels == 6:  # 5.1
        audio_params = "-c:a copy"
    else:  # 7.1 or higher
        audio_params = "-c:a ac3 -ac 6"  # Convert to 5.1
    
    cmd = f'ffmpeg -i "{input_file}" -c:v copy {audio_params} -sn "{output_file}"'
    
    try:
        subprocess.run(cmd, check=True)
        print(f"\nConversion complete! File saved to: {output_file}")
    except subprocess.CalledProcessError as e:
        print(f"\nError during conversion: {e}")
    
    input("\nPress Enter to continue...")
    clear_screen()

def main():
    run_as_admin()
    config = initialize_config()
    
    while True:
        choice = show_menu()
        
        if choice == "1":
            while True:
                installer_choice = show_installer_menu()
                if installer_choice == "1":
                    check_installations()
                elif installer_choice == "2":
                    clear_screen()
                    print("\nStarting installation...")
                    try:
                        download_ffmpeg(safe_install=True)
                    except Exception as e:
                        print(f"Error with safe install, trying alternative method...")
                        download_ffmpeg(safe_install=False)
                    try:
                        install_dmfs()
                    except Exception as e:
                        print(f"Error installing DMFS: {e}")
                    try:
                        install_dokan()
                    except Exception as e:
                        print(f"Error installing Dokan, contact support: {e}")
                    input("\nPress Enter to continue...")
                    clear_screen()
                elif installer_choice == "3":
                    while True:
                        clear_screen()
                        uninstall_choice = show_uninstall_menu()
                        if uninstall_choice in ["1", "2", "3"]:
                            if uninstall_choice == "1":
                                uninstall_ffmpeg()
                            elif uninstall_choice == "2":
                                uninstall_dmfs()
                            elif uninstall_choice == "3":
                                uninstall_ffmpeg()
                                uninstall_dmfs()
                            input("\nPress Enter to continue...")
                            clear_screen()
                            break
                        elif uninstall_choice == "4":
                            clear_screen()
                            break
                        else:
                            print("\nInvalid option. Please try again.")
                            input("Press Enter to continue...")
                elif installer_choice == "4":
                    clear_screen()
                    break
                else:
                    print("\nInvalid option. Please try again.")
                    input("Press Enter to continue...")
                    clear_screen()
                    
        elif choice == "2":
            handle_presets()
        elif choice == "3":
            # Crop Tool
            pass
        elif choice == "4":
            # Media Info
            pass
        elif choice == "5":
            convert_mkv_to_mp4(config)
        elif choice == "6":
            open_website()
        elif choice == "7":
            print("\nThank you for using the app. Goodbye!")
            sys.exit(0)
        else:
            print("\nInvalid option. Please try again.")
            input("Press Enter to continue...")
            clear_screen()

if __name__ == "__main__":
    main()
