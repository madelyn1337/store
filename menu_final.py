import os
import subprocess
import psutil
import platform
import sys
import time
import readline
import atexit
import requests
import zipfile
from pathlib import Path
import urllib.request
import shutil
from bs4 import BeautifulSoup
import threading
from rich.console import Console
import tempfile

console = Console()

def is_admin():
    if platform.system() == "Windows":
        import ctypes
        try:
            return ctypes.windll.shell32.IsUserAnAdmin()
        except:
            return False
    else:
        return os.geteuid() == 0

def run_as_admin():
    if not is_admin():
        if platform.system() == "Windows":
            import ctypes
            script = os.path.abspath(sys.argv[0])
            params = ' '.join(sys.argv[1:])
            ret = ctypes.windll.shell32.ShellExecuteW(None, "runas", sys.executable, f'"{script}" {params}', None, 1)
            if ret <= 32:
                raise Exception("Failed to elevate privileges")
            sys.exit(0)
        else:
            os.execvp('sudo', ['sudo', 'python3'] + sys.argv)
            sys.exit()

def is_ffmpeg_installed():
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

def install_media_info():
    try:
        if platform.system() == "Windows":
            url = "https://mediaarea.net/download/binary/mediainfo/24.01/MediaInfo_CLI_24.01_Windows_x64.zip"
            temp_path = os.path.join(os.getenv('TEMP'), "mediainfo.zip")
            print("Downloading MediaInfo...")
            response = requests.get(url)
            with open(temp_path, 'wb') as f:
                f.write(response.content)
            with zipfile.ZipFile(temp_path, 'r') as zip_ref:
                zip_ref.extractall(os.path.join(os.getenv('TEMP'), "mediainfo"))
            mediainfo_exe = os.path.join(os.getenv('TEMP'), "mediainfo", "mediainfo.exe")
            ffmpeg_dir = Path("C:/Program Files/ffmpeg")
            if ffmpeg_dir.exists():
                shutil.move(mediainfo_exe, ffmpeg_dir / "mediainfo.exe")
            shutil.rmtree(os.path.join(os.getenv('TEMP'), "mediainfo"))
            os.remove(temp_path)
        else:
            url = "https://github.com/madelyn1337/store/raw/refs/heads/main/mediainfo.pkg"
            temp_path = os.path.join(os.getenv('TEMP'), "mediainfo.pkg")
            response = requests.get(url)
            with open(temp_path, 'wb') as f:
                f.write(response.content)
            subprocess.run(["sudo", "installer", "-pkg", os.path.join(os.getenv('TEMP'), "mediainfo.pkg"), "-target", "/Applications"], check=True)
    except Exception as e:
        print(f"Error installing MediaInfo: {e}")

def is_dmfs_installed():
    program_files = Path("C:/Program Files/DebugMode/FrameServer")
    if program_files.exists():
        return True
    return False

def add_to_path(new_path):
    import winreg
    with winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, r'SYSTEM\CurrentControlSet\Control\Session Manager\Environment', 0, winreg.KEY_ALL_ACCESS) as key:
        path = winreg.QueryValueEx(key, 'Path')[0]
        if new_path not in path:
            new_path_value = f"{path};{new_path}"
            winreg.SetValueEx(key, 'Path', 0, winreg.REG_EXPAND_SZ, new_path_value)
            os.system('setx PATH "%PATH%"')
            print(f"Added {new_path} to PATH")

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
            if file.name in required_files: 
                dest = install_dir / file.name
                if dest.exists():
                    dest.unlink()
                file.rename(dest)
        add_to_path(str(install_dir))
    else:
        with zipfile.ZipFile(zip_path, 'r') as zip_ref:
            zip_ref.extractall("ffmpeg_temp")
        for file in required_files:
            source = f"ffmpeg_temp\\ffmpeg-master-latest-win64-gpl\\bin\\{file}"
            if os.path.exists(source):
                os.system(f'move "{source}" C:\\Windows\\System32')
    os.system('rmdir /S /Q ffmpeg_temp')
    os.remove(zip_path)

def install_dokan():
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

def install_dmfs():
    print("\nInstalling DMFS...")
    dmfs_dir = Path("C:/Program Files/DebugMode/FrameServer")
    adobe_dir = Path("C:/Program Files/Adobe/Common/Plug-ins/7.0/MediaCore")
    if not dmfs_dir.exists():
        dmfs_dir.mkdir(parents=True)
    if not adobe_dir.exists():
        adobe_dir.mkdir(parents=True) 
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
    except Exception as e:
        print(f"Error installing DMFS: {e}")

def open_website():
    website_link = "https://scenepacks.com" 
    os.system(f'start {website_link}')
    input("\nPress Enter to continue...")

def check_installations():
    clear_screen()
    print("\n=== Installation Status ===")
    print(f"FFmpeg: {'Installed ✓' if is_ffmpeg_installed() else 'Not Installed ✗'}")
    print(f"DMFS: {'Installed ✓' if is_dmfs_installed() else 'Not Installed ✗'}")
    input("\nPress Enter to continue...")
    clear_screen()

def uninstall_ffmpeg():
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

def uninstall_dmfs():
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

def install_all_3():
    clear_screen()
    download_ffmpeg()
    install_dmfs()
    install_media_info()

def uninstall_both():
    uninstall_ffmpeg()
    uninstall_dmfs()

def get_movie_details(url):
    try:
        response = requests.get(url)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, 'html.parser')
        details = {}
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
        audio_label = soup.find("span", class_="subheading", string="Audio")
        if audio_label:
            audio_section = audio_label.find_next("div", id="shortaudio")
            details["Audio"] = audio_section.get_text(strip=True, separator="\n") if audio_section else "N/A"
        else:
            details["Audio"] = "N/A"
        return details
    except Exception as e:
        import traceback
        traceback.print_exc()
        return {"Error": str(e)}

def get_video_folders():
    home_dir = os.path.expanduser("~")
    if platform.system() == "Darwin":
        videos_dir = os.path.join(home_dir, "Movies")
    else:
        videos_dir = os.path.join(home_dir, "Videos")
    folder_411 = os.path.join(videos_dir, "411")
    media_dir = os.path.join(folder_411, "Media")
    encoded_dir = os.path.join(folder_411, "Encoded")
    os.makedirs(media_dir, exist_ok=True)
    os.makedirs(encoded_dir, exist_ok=True)
    return folder_411, media_dir, encoded_dir

def detect_black_bars(video_path):
    try:
        ffprobe_command = [
            "ffmpeg", "-i", video_path, "-vf", "cropdetect=24:2:0",
            "-frames:v", "300", "-f", "null", "-" 
        ]
        result = subprocess.run(ffprobe_command, stderr=subprocess.PIPE, text=True)
        crop_lines = [line for line in result.stderr.split("\n") if "crop=" in line]
        if not crop_lines:
            return None
        last_crop = crop_lines[-1]
        crop_params = last_crop.split("crop=")[-1].split(" ")[0]
        try:
            w, h, x, y = map(int, crop_params.split(":"))
            if w <= 0 or h <= 0 or x < 0 or y < 0:
                return None
        except (ValueError, IndexError):
            return None
        return crop_params
    except Exception as e:
        return None

def set_preset():
    clear_screen()
    cpu_cores = psutil.cpu_count(logical=True)
    is_apple_silicon = (
        platform.system() == "Darwin" and 
        platform.processor() == "arm"
    )
    if is_apple_silicon:
        threads = min(cpu_cores - 2, 12)
        crf = 18
        x265_params = "aq-mode=3:aq-strength=0.9:psy-rd=2.0:deblock=-1,-1"
    _, _, output_dir = get_video_folders()
    readline.add_history(output_dir)
    if not os.path.isdir(output_dir):
        print("Invalid directory. Exiting.")
        return
    is_grainy = input("Is the movie extremely grainy (e.g., Texas Chainsaw Massacre)? (y/n): ").strip().lower()
    if cpu_cores > 20:
        threads = 28
        crf = 18
        x265_params = "aq-mode=3:aq-strength=0.9:psy-rd=2.0:deblock=-1,-1"
    elif 16 < cpu_cores <= 20:
        threads = 18
        crf = 18
        x265_params = "psy-rd=2.0:deblock=-1,-1"
    elif 10 < cpu_cores <= 16:
        threads = 14
        crf = 20
        x265_params = "psy-rd=1.0:deblock=-1,-1"
    elif 5 < cpu_cores <= 10:
        threads = 6
        crf = 20
        x265_params = "deblock=-1,-1"
    else:
        threads = 4
        crf = 20
        x265_params = None
    if is_grainy == 'y':
        crf -= 2
    x265_params_str = f'-x265-params "{x265_params}"' if x265_params else ""
    ffmpeg_command = (
        f'ffpb -i C:/DMFS/virtual/*.avi -c:v libx265 -preset medium -crf {crf} '
        f'-tune grain {x265_params_str} '
        f'-c:a aac -b:a 576K -ac 2 -ar 48000 -sn -threads {threads} '
        f'-tag:v hvc1 -pix_fmt yuv420p -movflags +faststart '
        f'-metadata scenepack by=411 '
        f'"{output_dir}/encoded.mp4"'
    )
    if platform.system() == "Windows":
        reg_path = r"SOFTWARE\DebugMode\FrameServer"
        import winreg
        try:
            with winreg.CreateKey(winreg.HKEY_CURRENT_USER, reg_path) as key:
                winreg.SetValueEx(key, "runCommandOnFsStart", 0, winreg.REG_DWORD, 1)
                winreg.SetValueEx(key, "endAfterRunningCommand", 0, winreg.REG_DWORD, 1)
                winreg.SetValueEx(key, "pcmAudioInAvi", 0, winreg.REG_DWORD, 1)
                winreg.SetValueEx(key, "commandToRunOnFsStart", 0, winreg.REG_SZ, ffmpeg_command)
        except PermissionError:
            print("Error: Run the script with administrator privileges to modify registry keys.")

def full_ffmpeg_access():
    print("Enter your custom FFmpeg command:")
    custom_command = input().strip()
    reg_path = r"SOFTWARE\DebugMode\FrameServer"
    import winreg
    try:
        with winreg.CreateKey(winreg.HKEY_CURRENT_USER, reg_path) as key:
            winreg.SetValueEx(key, "commandToRunOnFsStart", 0, winreg.REG_SZ, custom_command)
        print("Custom FFmpeg command has been set.")
    except PermissionError:
        print("Error: Run the script with administrator privileges to modify registry keys.")

def get_file_path(prompt_message="Drag and drop the file here and press Enter:"):
    if platform.system() == "Windows":
        # Create a temporary file to store the file path
        temp_file = tempfile.NamedTemporaryFile(delete=False)
        temp_file.close()

        # Use 'runas' to open a non-admin command prompt
        subprocess.Popen(
            f'runas /user:{os.getenv("USERNAME")} "cmd /k echo {prompt_message} & set /p filepath= & echo %filepath% > {temp_file.name} & exit"',
            shell=True
        )

        input("Press Enter after dragging and dropping the file in the new window...")

        # Read the file path from the temporary file
        with open(temp_file.name, 'r') as f:
            file_path = f.read().strip()

        # Clean up the temporary file
        os.remove(temp_file.name)

        if not os.path.isfile(file_path):
            print(f"Invalid file path: {file_path}")
            return None

        return file_path
    else:
        # Handle other platforms if needed
        pass

def mkv_to_mp4():
    clear_screen()
    folder_411, media_dir, encoded_dir = get_video_folders()
    video_path = get_file_path("Drag and drop the video file here and press Enter:")
    if not video_path:
        main()
        return
    readline.add_history(video_path)
    if not os.path.isfile(video_path):
        print(f"Invalid file path: {video_path}")
        return
    clear_screen()
    print("Choose conversion method:")
    print("\n1. Fast copy to MP4 (no cropping, maintains original quality)")
    print("\n2. Re-encode to ProRes with automatic black bar detection/cropping")
    print("\n3. Re-encode to H.264")
    choice = input("\nEnter choice (1, 2, 3, or 'q' to go back): ").strip()
    if choice.lower() == 'q':
        main()
        return
    clear_screen()
    input_filename = os.path.splitext(os.path.basename(video_path))[0]
    threads = str(min(psutil.cpu_count(logical=True) - 2, 12))
    try:
        audio_streams = subprocess.check_output(
            ["ffprobe", "-v", "error", "-select_streams", "a", "-show_entries", "stream=channels", "-of", "csv=p=0", video_path],
            text=True
        ).strip().split('\n')
        audio_map = "0:a:0"
        for i, channels in enumerate(audio_streams):
            if channels.strip() == "6":
                audio_map = f"0:a:{i}"
                break
            elif channels.strip() == "8":
                audio_map = f"0:a:{i}"
                downmix = True
                break
        if choice == "1":
            output_path = os.path.join(media_dir, f"{input_filename}.mp4")
            probe_cmd = ["ffprobe", "-v", "error", "-select_streams", "v:0", 
                        "-show_entries", "stream=codec_name", "-of", "default=noprint_wrappers=1:nokey=1", 
                        video_path]
            codec = subprocess.check_output(probe_cmd, text=True).strip()
            tag = "hvc1" if codec == "hevc" else "avc1" if codec == "h264" else None
            ffmpeg_command = [
                "ffpb", "-i", video_path,
                "-map", "0:v:0",
                "-map", audio_map,
                "-c:v", "copy",
                "-tag:v", tag,
                "-c:a", "copy",
                "-sn",
                "-threads", threads,
                output_path
            ]
        if choice == "2":
            while True:
                print("Choose ProRes profile:")
                print("\n1. Proxy (Recommended)")
                print("\n2. LT")
                print("\n3. 422")
                print("\n4. 422 HQ")
                print("\n5. 4444")
                print("\n6. 4444 XQ")
                print("\n7. Info about each codec")
                profile_choice = input("\nEnter choice (1-7): ").strip()
                if profile_choice == "7":
                    clear_screen()
                    print("ProRes Profiles Information:")
                    print("\nProRes in general is a extremely fast codec to encode and edit with.")
                    print("\nWhen increasing the profile, it generally increases the quality and file size although speed really isnt affected THAT much.")
                    print("\nHowever going TOO high actually just doesnt make that big of a difference to the human eyes and just makes file size WAY too big.")
                    print("\nFor 40 min shows just divide the file size by roughly 3 - 3.5")                
                    print("\n1. Proxy: Low bitrate, lowest file size. 2 hour movie 1080p: ~45GB 4k: ~180GB")
                    print("\n2. LT: Lower bitrate than 422, good for editing. 2 hour movie 1080p: ~60GB 4k: ~240GB")
                    print("\n3. 422: Standard quality, widely used for editing. 2 hour movie 1080p: ~100GB 4k: ~400GB")
                    print("\n4. 422 HQ: Higher quality than 422, used for high-end editing. 2 hour movie 1080p: ~120GB 4k: ~500GB")
                    print("\n5. 4444: Supports alpha channel, used for compositing. 2 hour movie 1080p: ~180GB 4k: ~720GB")
                    print("\n6. 4444 XQ: Highest quality, supports alpha channel. 2 hour movie 1080p: ~240GB 4k: ~960GB")
                    input("\nPress any key to continue...")
                    clear_screen()
                else:
                    break
            output_path = os.path.join(media_dir, f"{input_filename}.mov")
            crop_params = detect_black_bars(video_path)
            ffmpeg_command = [
                "ffpb", "-i", video_path,
                "-map", "0:v:0",
                "-map", audio_map,
                "-c:v", "prores_ks",
                "-profile:v", "0",
                "-vendor", "apl0",
                "-pix_fmt", "yuv422p10le"
            ]
            if crop_params:
                ffmpeg_command.extend(["-vf", f"crop={crop_params}"])
            ffmpeg_command.extend([
                "-c:a", "pcm_s24le",
                "-sn",
                "-threads", threads,
                "-metadata", "scenepack by=411",
                output_path
            ])
        if choice == "3":
            output_path = os.path.join(media_dir, f"{input_filename}_h264.mp4")
            ffmpeg_command = [
                "ffpb", "-i", video_path,
                "-map", "0:v:0",
                "-map", audio_map,
                "-c:v", "libx264",
                "-preset", "medium",
                "-crf", "8",
                "-c:a", "pcm_s24le",
                "-sn",
                "-threads", threads,
                "-metadata", "scenepack by=411",
                output_path
            ]
        else:
            print("Invalid choice. Please enter 1, 2, or 3.")
            return
        subprocess.run(ffmpeg_command, check=True)
        print("Conversion complete!")
    except subprocess.CalledProcessError as e:
        print(f"Conversion failed! Error: {e}")
    except Exception as e:
        print(f"An error occurred: {e}")

def clear_screen():
    os.system('cls' if platform.system() == "Windows" else 'clear')

def show_easter_egg():
    import time
    frames = [
        """
                     +++++     +++++                     
                     +++++     +++++                     
                     +++++     +++++                     
                     +++++     +++++                     
                     +++++     +++++                     
                     +++++     +++++                     
                     +++++     +++++                     
                     +++++     +++++                     
      ++++++++++++++++++++++++++++++++++++++++++++++     
       ++++++++++++++++++++++++++++++++++++++++++++      
        +++++++++++++++++++++++++++++++++++++++++        
          ++++++     +++++     +++++     ++++++          
           ++++++    +++++     +++++    ++++++           
             ++++++  +++++     +++++  ++++++             
               +++++ +++++     +++++ ++++++              
                ++++++++++     ++++++++++                
                 +++++++++     +++++++++                 
                   +++++++     +++++++                   
                     +++++     +++++                     
                      ++++     ++++                      
                        ++     +++                       
                         +     +                         
        """,
        """
                     ░░░░░     ░░░░░                     
                     ░░░░░     ░░░░░                     
                     ░░░░░     ░░░░░                     
                     ░░░░░     ░░░░░                     
                     ░░░░░     ░░░░░                     
                     ░░░░░     ░░░░░                     
                     ░░░░░     ░░░░░                     
                     ░░░░░     ░░░░░                     
      ░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░     
       ░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░      
        ░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░        
          ░░░░░░     ░░░░░     ░░░░░     ░░░░░░          
           ░░░░░░    ░░░░░     ░░░░░    ░░░░░░           
             ░░░░░░  ░░░░░     ░░░░░  ░░░░░░             
               ░░░░░ ░░░░░     ░░░░░ ░░░░░              
                ░░░░░░░░░░     ░░░░░░░░░░                
                 ░░░░░░░░░     ░░░░░░░░░                 
                   ░░░░░░░     ░░░░░░░                   
                     ░░░░░     ░░░░░                     
                      ░░░░     ░░░░                      
                        ░░     ░░░                       
                         ░     ░                         
        """
    ]
    if platform.system() == "Windows":
        import ctypes
        ctypes.windll.user32.MessageBoxW(0, "You found the secret! 411", "Easter Egg", 0)
    clear_screen()
    print("🎮 You found the secret! 🎮")
    for _ in range(5):
        for frame in frames:
            print("\033[H")
            print(frame)
            print("\n411 Easter Egg Found! 🎉")
            time.sleep(0.5)
    print("\nCongratulations! You discovered the Windows 11 easter egg! 🎉")
    time.sleep(2)
    main()

def media_info():
    def check_mediainfo():
        try:
            subprocess.run(['mediainfo', '--version'], capture_output=True)
            return True
        except FileNotFoundError:
            return False
    if not check_mediainfo():
        print("MediaInfo not found. Installing MediaInfo...")
        install_media_info()
        if not check_mediainfo():
            print("Failed to install MediaInfo. Please try installing manually.")
            input("\nPress Enter to continue...")
            return
    clear_screen()
    file_path = get_file_path("Drag and drop a media file here and press Enter:")
    if not file_path:
        return
    try:
        result = subprocess.run(['mediainfo', file_path], capture_output=True, text=True)
        clear_screen()
        print("\nMediaInfo Analysis Results:\n")
        print(result.stdout)
        input("\nPress Enter to continue...")
        clear_screen()
    except Exception as e:
        print(f"\nError running MediaInfo: {e}")
        input("\nPress Enter to continue...")
        clear_screen()

def media_tools():
    clear_screen()
    print("Media Tools Menu")
    print("\n1. MediaInfo")
    print("\n2. BluRay/WEB Info")
    print("\n3. Go Back")
    choice = input("\nEnter your choice: ").strip()
    if choice == "1":
        clear_screen()
        media_info()
    elif choice == "2":
        clear_screen()
        print("\nEnter the Blu-ray.com URL: ")
        url = input().strip()
        if url:
            details = get_movie_details(url)
            if "Error" in details:
                print(f"\nError: {details['Error']}")
            else:
                clear_screen()
                print("\nVideo Details:")
                print(details.get("Video", "N/A"))
                print("\nAudio Details:")
                print(details.get("Audio", "N/A"))
            input("\nPress Enter to continue...")
            clear_screen()
    elif choice == "3":
        main()

def installers_and_uninstallers():
    clear_screen()
    print("Installers & Uninstallers Menu")
    print("\n1. Install All 3")
    print("\n2. Install FFmpeg")
    print("\n3. Install DMFS")
    print("\n4. Install MediaInfo")
    print("\n5. Uninstall Both")
    print("\n6. Uninstall DMFS")
    print("\n7. Uninstall FFmpeg")
    choice = input("\nEnter your choice: ").strip()
    if choice == "1":
        install_all_3()
    elif choice == "2":
        download_ffmpeg()
    elif choice == "3":
        install_dmfs()
    elif choice == "4":
        install_media_info()
    elif choice == "5":
        uninstall_both()
    elif choice == "6":
        uninstall_dmfs()
    elif choice == "7":
        uninstall_ffmpeg()

def generate_usage_bars():
    bar_length = 30
    default_bar_color = "#9656ce"
    high_usage_color = "#FF0000"
    mem = psutil.virtual_memory()
    mem_usage = mem.percent
    cpu_usage = psutil.cpu_percent()
    mem_bar_color = default_bar_color if mem_usage <= 90 else high_usage_color
    cpu_bar_color = default_bar_color if cpu_usage <= 90 else high_usage_color
    mem_filled = f"[{mem_bar_color}]/[/{mem_bar_color}]" * int(bar_length * mem_usage // 100)
    mem_empty = "[white]/[/white]" * (bar_length - int(bar_length * mem_usage // 100))
    mem_bar = f"[ {mem_filled}{mem_empty} ]"
    cpu_filled = f"[{cpu_bar_color}]/[/{cpu_bar_color}]" * int(bar_length * cpu_usage // 100)
    cpu_empty = "[white]/[/white]" * (bar_length - int(bar_length * cpu_usage // 100))
    cpu_bar = f"[ {cpu_filled}{cpu_empty} ]"
    console.clear()
    percentage_color = "#5865F2"
    console.print(f"Mem% -= {mem_bar} =- [bold {percentage_color}]{mem_usage:.2f}%[/bold {percentage_color}]")
    console.print(f"CPU% -= {cpu_bar} =- [bold {percentage_color}]{cpu_usage:.2f}%[/bold {percentage_color}]")
    
    if platform.system() == "Darwin":
        partitions = [psutil.disk_partitions()[0]]  # Only main drive
    else:
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
                f"Drive {partition.device} -= {disk_bar} =- [bold {percentage_color}]{disk_usage:.2f}%[/bold {percentage_color}]"
            )
        except PermissionError:
            console.print(f"Drive {partition.device} - [bold red]Access Denied[/bold red]")

def main():
    run_as_admin()
    while True:
        generate_usage_bars()
        print("\n")
        print("\n")
        print("====================================")
        print("               CLI                  ")
        print("====================================")
        print("1. Installers & Uninstallers")
        print("2. Set Preset")
        print("3. Convert MKV to MP4")
        print("4. Media Tools")
        print("5. 411 Website")
        print("6. Exit")
        print("====================================")
        choice = input("\nEnter your choice: ").strip()
        if choice == "411":
            show_easter_egg()
        elif choice == "secretcode":
            full_ffmpeg_access()
        elif choice == "1":
            installers_and_uninstallers()
        elif choice == "2":
            set_preset()
        elif choice == "3":
            mkv_to_mp4()
        elif choice == "4":
            media_tools()
        elif choice == "5":
            open_website()
        elif choice == "6" or choice.lower() == 'q':
            clear_screen()
            print("Goodbye.")
            sys.exit()
        else:
            print("Invalid choice.")
            time.sleep(1)

if __name__ == "__main__":
    main()
