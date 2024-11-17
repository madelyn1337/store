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
        
        subprocess.run(exe_path, shell=True)
        
        os.remove(exe_path)
        
        input("\nPress Enter to continue to menu...")
        clear_screen()
        
    except Exception as e:
        return

def show_menu():
    clear_screen()
    print("\n=== Main Menu ===")
    print("1. Installation Options")
    print("2. Neofetch")
    print("3. Presets")
    print("4. Crop Tool")
    print("5. Movie Info")
    print("6. 411 Website")
    print("7. Exit")
    return input("\nPlease select an option (1-7): ")

def show_installer_menu():
    clear_screen()
    print("\n=== Installation Options ===")
    print("1. Check Installed Components")
    print("2. Install All Components")
    print("3. Uninstall Components")
    print("4. Back to Main Menu")
    return input("\nPlease select an option (1-4): ")

def show_uninstall_menu():
    print("\n=== Uninstall Components ===")
    print("1. Uninstall FFmpeg")
    print("2. Uninstall DMFS")
    print("3. Uninstall Both")
    print("4. Back to Main Menu")
    return input("\nPlease select an option (1-4): ")

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
    website_link = "https://scenepacks.com/" 
    print("\nOpening website in your browser...")
    os.system(f'start {website_link}')
    input("\nPress Enter to continue...")

def is_ffmpeg_installed():
    paths = os.environ["PATH"].split(os.pathsep)
    for path in paths:
        ffmpeg_path = os.path.join(path, "ffmpeg.exe")
        if os.path.exists(ffmpeg_path):
            return True
            
    program_files_path = Path("C:/Program Files/ffmpeg/ffmpeg.exe")
    if program_files_path.exists():
        return True
        
    system32_path = Path("C:/Windows/System32/ffmpeg.exe")
    if system32_path.exists():
        return True

    c_path = Path("C:/ffmpeg/ffmpeg.exe")
    if c_path.exists():
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
        print("Downloading Dokan...")
        urllib.request.urlretrieve(dokan_url, msi_path)
        
        # Silent install using msiexec
        print("Installing Dokan silently...")
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
        print(f"Created directory: {dmfs_dir}")
    else:
        print(f"Directory already exists: {dmfs_dir}")
        
    if not adobe_dir.exists():
        adobe_dir.mkdir(parents=True) 
        print(f"Created directory: {adobe_dir}")
    else:
        print(f"Directory already exists: {adobe_dir}")

    extension_url = "https://github.com/madelyn1337/store/raw/refs/heads/main/dfscPremiereOut.prm"
    zip_url = "https://github.com/madelyn1337/store/raw/refs/heads/main/FrameServer.zip"
    
    try:
        # Download extension
        print("Downloading extension...")
        extension_path = adobe_dir / "dfscPremiereOut.prm"
        urllib.request.urlretrieve(extension_url, extension_path)
        
        # Download and extract zip
        print("Downloading and extracting DMFS files...")
        zip_path = "FrameServer.zip"
        urllib.request.urlretrieve(zip_url, zip_path)
        
        with zipfile.ZipFile(zip_path, 'r') as zip_ref:
            zip_ref.extractall(dmfs_dir)
        
        os.remove(zip_path)
        print("DMFS installation complete!")
        
    except Exception as e:
        print(f"Error installing DMFS: {e}")

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
    
    if safe_install:
        install_dir = Path("C:/Program Files/ffmpeg")
        install_dir.mkdir(parents=True, exist_ok=True)
        
        with zipfile.ZipFile(zip_path, 'r') as zip_ref:
            zip_ref.extractall("ffmpeg_temp")
        
        bin_path = Path("ffmpeg_temp/ffmpeg-master-latest-win64-gpl/bin")
        for file in bin_path.glob('*'):
            dest = install_dir / file.name
            if dest.exists():
                dest.unlink()
            file.rename(dest)
        
        add_to_path(str(install_dir))
    else:
        with zipfile.ZipFile(zip_path, 'r') as zip_ref:
            zip_ref.extractall("ffmpeg_temp")
        
        os.system('move ffmpeg_temp\\ffmpeg-master-latest-win64-gpl\\bin\\* C:\\Windows\\System32')
    
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
    
    # Get movie file
    filepath = input("Enter the full path to your movie file: ")
    if not os.path.exists(filepath):
        print("File not found!")
        input("\nPress Enter to continue...")
        return
    
    # Get video resolution
    width, height = get_video_info(filepath)
    if not width or not height:
        print("Could not determine video resolution!")
        input("\nPress Enter to continue...")
        return
    
    # Extract movie name and search IMDb
    movie_name = os.path.basename(filepath)
    print(f"\nSearching IMDb for: {movie_name}")
    
    try:
        # Use functions from test.py
        from test import get_imdb_id, get_technical_details
        imdb_id = get_imdb_id(movie_name)
        if not imdb_id:
            imdb_id = input("Could not find IMDb ID. Please enter it manually (ttXXXXXXX): ")
        
        aspect_ratios, negative_formats = get_technical_details(imdb_id)
        
        # Display found information
        print(f"\nVideo Resolution: {width}x{height}")
        print("Aspect Ratios:", ", ".join([ar[0] for ar in aspect_ratios]) if aspect_ratios else "Unknown")
        print("Format:", ", ".join(negative_formats) if negative_formats else "Unknown")
        
        # Ask for grain level
        print("\nGrain Levels:")
        print("1. No Grain")
        print("2. With Grain")
        print("3. Heavy Grain")
        grain_level = input("Select grain level (1-3): ")
        
        # Update registry with placeholder command
        reg_path = r"SOFTWARE\DebugMode\FrameServer"
        with winreg.OpenKey(winreg.HKEY_CURRENT_USER, reg_path, 0, winreg.KEY_WRITE) as key:
            placeholder_command = "ffmpeg -placeholder command"  # Replace with actual preset commands
            winreg.SetValueEx(key, "commandToRunOnFsStart", 0, winreg.REG_SZ, placeholder_command)
        
        print("\nPreset applied successfully!")
        
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
    
    # Base widths for each resolution
    resolutions = {
        "2160p": 3840,
        "1080p": 1920
    }
    
    # Common aspect ratios with their names
    aspect_ratios = {
        "1.33": "4:3",
        "1.37": "Academy",
        "1.66": "5:3",
        "1.78": "16:9",
        "1.85": "Flat",
        "1.90": "",
        "2.00": "",
        "2.35": "",
        "2.37": "64:27",
        "2.39": "DCI Scope",
        "2.40": "Blu-Ray Scope",
        "2.44": ""
    }
    
    resolution = ""
    aspect_ratio = ""
    
    for line in video_info.split("\n"):
        if "1080p" in line:
            resolution = "1080p"
        elif "2160p" in line:
            resolution = "2160p"
        if ":" in line:
            for ratio in aspect_ratios.keys():
                if ratio in line:
                    aspect_ratio = ratio
                    break
    
    if resolution and aspect_ratio:
        width = resolutions[resolution]
        height = round(width / float(aspect_ratio))
        
        ratio_name = aspect_ratios[aspect_ratio]
        ratio_display = f" ({ratio_name})" if ratio_name else ""
        
        print(f"\nResolution: {resolution}")
        print(f"Aspect Ratio: {aspect_ratio}:1{ratio_display}")
        print("\nRecommended timeline settings:")
        print(f"Width: {width}")
        print(f"Height: {height}")
    else:
        print("Could not determine resolution or aspect ratio from the provided URL.")


def main():
    run_as_admin()
    neofetch()

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
            neofetch()
        elif choice == "3":
            handle_presets()
        elif choice == "4":
            clear_screen()
            url = input("\nEnter the movie URL from scenepacks.com: ")
            if url:
                details = get_movie_details(url)
                if "Error" not in details:
                    calculate_crop(details)
                else:
                    print(f"\nError fetching movie details: {details['Error']}")
            input("\nPress Enter to continue...")
            clear_screen()
            
        elif choice == "5":
            clear_screen()
            url = input("\nEnter the movie URL from scenepacks.com: ")
            if url:
                details = get_movie_details(url)
                if "Error" not in details:
                    print("\nVideo Details:")
                    print(details["Video"])
                    print("\nAudio Details:")
                    print(details["Audio"])
                else:
                    print(f"\nError fetching movie details: {details['Error']}")
            input("\nPress Enter to continue...")
            clear_screen()
            
        elif choice == "6":
            open_website()
            clear_screen()
            
        elif choice == "7":
            print("\nThank you for using the app. Goodbye!")
            sys.exit(0)
            
        else:
            print("\nInvalid option. Please try again.")
            input("Press Enter to continue...")
            clear_screen()

if __name__ == "__main__":
    main()
