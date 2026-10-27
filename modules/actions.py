print("=== ACTIONS.PY LOADED ===")

import os
import re
import webbrowser
import psutil
import time
from datetime import datetime
from PIL import ImageGrab
from modules.battery import get_battery_status
from modules.ollama_chat import ask_ai
from modules.voice import speak
from modules.weather import get_weather
from modules.system_info import (
    get_system_info,
    get_short_system_info,
    get_system_health,
    get_running_processes,
    get_top_cpu_processes,
    get_top_memory_processes,
    get_cpu_health,
    get_ram_health,
    get_disk_health,
    get_detailed_system_health,
    diagnose_slow_system_detailed,
    get_complete_slow_system_report,
    get_troubleshooting_report,
    get_running_applications,
    get_application_resource_usage,
    get_resource_history_analysis,
    detect_resource_spike,
    detect_repeated_resource_spikes,
    detect_resource_trend,
    get_combined_resource_intelligence,
    close_application
)
from modules.apps import open_app
from modules.file_manager import (
    create_folder,
    create_text_file,
    open_file_or_folder,
    write_to_file,
    add_to_file,
    read_file,
    delete_file_or_folder,
    search_files
)
from modules.volume import (
    get_volume,
    set_volume,
    increase_volume,
    decrease_volume,
    mute_volume,
    unmute_volume
)
from modules.brightness import (
    get_brightness,
    set_brightness,
    increase_brightness,
    decrease_brightness
)
# =====================================================
# APPLICATION ALIASES
# =====================================================

APP_ALIASES = {

    "chrome": [
        "chrome",
        "google chrome",
        "browser",
        "web browser"
    ],

    "edge": [
        "edge",
        "microsoft edge",
        "microsoft browser"
    ],

    "vscode": [
        "vs code",
        "visual studio code",
        "code",
        "coding",
        "code editor"
    ],

    "notepad": [
        "notepad",
        "text editor",
        "text editing"
    ],

    "calculator": [
        "calculator",
        "calc",
        "math calculator"
    ],

    "paint": [
        "paint",
        "microsoft paint",
        "drawing app"
    ],

    "explorer": [
        "file explorer",
        "windows explorer",
        "explorer",
        "files"
    ]
}
# =====================================================
# SYSTEM CONTROL CONFIRMATION
# =====================================================

pending_system_action = None
pending_system_action_time = None
# =====================================================
# FIND APPLICATION FROM ALIAS
# =====================================================

def find_application_alias(command):

    command = command.lower().strip()

    for app_name, aliases in APP_ALIASES.items():

        for alias in aliases:

            if alias in command:

                return app_name

    return None
def open_folder(folder_name):
    user = os.environ["USERPROFILE"]
    one_drive = os.environ.get("OneDrive")

    paths = [
        os.path.join(user, folder_name),
    ]

    if one_drive:
        paths.append(os.path.join(one_drive, folder_name))

    for path in paths:
        if os.path.exists(path):
            os.startfile(path)
            return True

    return False
# =====================================================
# COMMAND NORMALIZATION
# =====================================================
def normalize_command(command):
    command = command.lower().strip()
    replacements = {
        "what's": "what is",
        "whats": "what is",
        "who's": "who is",
        "wheres": "where is",
        "where's": "where is",
        "can't": "cannot",
        "could you": "",
        "can you": "",
        "please": "",
        "for me": ""
    }
    for old, new in replacements.items():
        command = command.replace(old, new)
    command = " ".join(command.split())
    return command
def matches_intent(command, keywords):
    return all(word in command for word in keywords)
def matches_any_intent(command, keywords):
    return any(word in command for word in keywords)
def matches_intent_groups(command, groups):
    return all(any(word in command for word in group) for group in groups)
def execute(command):
    from modules.desktop_control import handle_notepad
    result = handle_notepad(command)
    if result is not None:
        speak(result)
        return
    global pending_system_action
    global pending_system_action_time
    command = normalize_command(command)
    print("Normalized command:", command)
    # Route exact application requests before desktop-file searches.
    app_requests = {
        "open notepad": "notepad", "launch notepad": "notepad",
        "start notepad": "notepad", "open note pad": "notepad",
        "open calculator": "calculator", "open calc": "calculator",
        "open paint": "paint", "open command prompt": "command prompt",
        "open cmd": "cmd", "open powershell": "powershell",
    }
    if command in app_requests:
        result = open_app(app_requests[command])
        speak(result or "I couldn't open that application.")
        return
    # =================================================
    # SYSTEM ACTION CONFIRMATION
    # =================================================

    if pending_system_action:

        # Confirmation expires after 10 seconds

        if (
            pending_system_action_time
            and time.time() - pending_system_action_time > 10
        ):

            pending_system_action = None
            pending_system_action_time = None

            speak(
                "The confirmation expired. "
                "I cancelled the action."
            )

            return

        if command in [
            "yes",
            "yeah",
            "yep",
            "s",
            "confirm",
            "do it"
        ]:

            action = pending_system_action

            pending_system_action = None
            pending_system_action_time = None

            if action == "restart":

                speak( "Restarting your computer")
                
                os.system("shutdown /r /t 5")
                return

            elif action == "shutdown":

                speak( "Shutting down your computer")

                os.system("shutdown /s /t 5" )

                return
            elif action == "sleep":
            
                speak(   "Putting your computer to sleep"  )
            
                os.system( "rundll32.exe powrprof.dll,SetSuspendState 0,1,0" )
            
                return

        elif command in [
            "no",
            "nope",
            "cancel",
            "don't"
        ]:

            pending_system_action = None
            pending_system_action_time = None

            speak(
                "Okay, I cancelled that action."
            )

            return

    # =====================================================
    # EXIT
    # =====================================================
    if "exit" in command or "quit" in command or "stop" in command:

        speak("See You Sam")
        print("See You SAM!")
        exit()

   # =====================================================
   # OPEN APPLICATIONS
   # =====================================================

    elif "open" in command and find_application_alias(command) is not None:

     smart_app = find_application_alias(command)

     if smart_app == "chrome":

        speak("Opening Chrome")
        os.system("start chrome")

     elif smart_app == "edge":

        speak("Opening Microsoft Edge")
        os.system("start microsoft-edge")

     elif smart_app == "vscode":

        speak("Opening Visual Studio Code")
        os.system("code")

     elif smart_app == "notepad":

        speak("Opening Notepad")
        os.system("notepad")

     elif smart_app == "calculator":

        speak("Opening Calculator")
        os.system("calc")

     elif smart_app == "paint":

        speak("Opening Paint")
        os.system("mspaint")

     elif smart_app == "explorer":

        speak("Opening File Explorer")
        os.system("explorer")

     else:

        speak("I don't know how to open that application.")

    elif "task manager" in command:

        speak("Opening Task Manager")
        os.system("taskmgr")

    elif "command prompt" in command or command == "open cmd":

        speak("Opening Command Prompt")
        os.system("start cmd")

    elif "powershell" in command:

        speak("Opening PowerShell")
        os.system("start powershell")

    elif "settings" in command:

        speak("Opening Settings")
        os.system("start ms-settings:")

    elif command in ("youtube", "open youtube"):

        speak("Opening YouTube")
        webbrowser.open("https://www.youtube.com")

    # =====================================================
# YOUTUBE SEARCH
# =====================================================

    elif (
     command.startswith("search youtube ")
     or command.startswith("youtube search ")
     or command.startswith("youtube ")
):

     if command.startswith("search youtube for "):

        search_query = command.replace(
            "search youtube for ", "", 1
        ).strip()

     elif command.startswith("search youtube "):

        search_query = command.replace(
            "search youtube ", "", 1
        ).strip()

     elif command.startswith("youtube search "):

        search_query = command.replace(
            "youtube search ", "", 1
        ).strip()

     else:

        search_query = command.replace(
            "youtube ", "", 1
        ).strip()

     if search_query:

        print(
            f"Searching YouTube for: {search_query}"
        )

        speak(
            f"Searching YouTube for {search_query}"
        )

        search_url = (
            "https://www.youtube.com/results?search_query="
            + search_query.replace(" ", "+")
        )

        webbrowser.open(search_url)

     else:

        speak(
            "What would you like me to search for on YouTube?"
        )


# =====================================================
# WEBSITE SEARCH
# =====================================================

    elif command.startswith("search wikipedia for "):

     search_query = command.replace(
        "search wikipedia for ", "", 1
     ).strip()

     if search_query:

        speak(
            f"Searching Wikipedia for {search_query}"
        )

        search_url = (
            "https://en.wikipedia.org/w/index.php?search="
            + search_query.replace(" ", "+")
        )

        webbrowser.open(search_url)


    elif command.startswith("search github for "):

     search_query = command.replace(
        "search github for ", "", 1
     ).strip()

     if search_query:

        speak(
            f"Searching GitHub for {search_query}"
        )

        search_url = (
            "https://github.com/search?q="
            + search_query.replace(" ", "+")
        )

        webbrowser.open(search_url)


    elif command.startswith("search amazon for "):

     search_query = command.replace(
        "search amazon for ", "", 1
     ).strip()

     if search_query:

        speak(
            f"Searching Amazon for {search_query}"
        )

        search_url = (
            "https://www.amazon.in/s?k="
            + search_query.replace(" ", "+")
        )

        webbrowser.open(search_url)


# =====================================================
# WEB SEARCH
# =====================================================

    elif (
     command.startswith("search ")
     or command.startswith("search for ")
     or command.startswith("google ")
     or command.startswith("search the web for ")
     or command.startswith("search the internet for ")
     or command.startswith("search the internet of ")
     or command.startswith("look up ")
     or command.startswith("lookup ")
):

     if command.startswith("search the web for "):

        search_query = command.replace(
            "search the web for ", "", 1
        ).strip()

     elif command.startswith("search the internet for "):

        search_query = command.replace(
            "search the internet for ", "", 1
        ).strip()

     elif command.startswith("search the internet of "):

        search_query = command.replace(
            "search the internet of ", "", 1
        ).strip()
 
     elif command.startswith("search for "):

        search_query = command.replace(
            "search for ", "", 1
        ).strip()

     elif command.startswith("search "):

        search_query = command.replace(
            "search ", "", 1
        ).strip()

     elif command.startswith("google "):

        search_query = command.replace(
            "google ", "", 1
        ).strip()

     elif command.startswith("look up "):

        search_query = command.replace(
            "look up ", "", 1
        ).strip()

     else:

        search_query = command.replace(
            "lookup ", "", 1
        ).strip()

     if search_query:

        print(
            f"Searching Google for: {search_query}"
        )

        speak(
            f"Searching Google for {search_query}"
        )

        search_url = (
            "https://www.google.com/search?q="
            + search_query.replace(" ", "+")
        )

        webbrowser.open(search_url)

     else:

        speak(
            "What would you like me to search for?"
        )
    # =====================================================
    # OPEN WINDOWS FOLDERS
    # =====================================================

    elif "open desktop" in command:

     speak("Opening Desktop")

     if not open_folder("Desktop"):
        speak("Desktop folder not found.")

    elif "open downloads" in command:

     speak("Opening Downloads")

     if not open_folder("Downloads"):
        speak("Downloads folder not found.")

    elif "open documents" in command:

     speak("Opening Documents")

     if not open_folder("Documents"):
        speak("Documents folder not found.")

    elif "open pictures" in command:

     speak("Opening Pictures")

     if not open_folder("Pictures"):
        speak("Pictures folder not found.")

    elif "open videos" in command:

     speak("Opening Videos")

     if not open_folder("Videos"):
        speak("Videos folder not found.")

    elif "open music" in command:

     speak("Opening Music")

     if not open_folder("Music"):
        speak("Music folder not found.")
    # =====================================================
# WRITE TEXT TO FILE
# =====================================================

    elif "write " in command and " in " in command:

     try:

        parts = command.split(" in ", 1)

        text_part = parts[0].replace("write ", "", 1).strip()
        file_name = parts[1].strip()

        if text_part and file_name:

            print(f"Writing: {text_part}")
            print(f"File: {file_name}")

            result = write_to_file(file_name, text_part)

            print(result)

            speak(result)

        else:

            speak("Please tell me what to write and which file to use.")

     except Exception as e:

        print("Write Error:", e)

        speak("Sorry, I couldn't write to the file.")
    # =====================================================
# ADD TEXT TO FILE
# =====================================================

    elif "add " in command and " to " in command:

      try:

        parts = command.split(" to ", 1)

        text_part = parts[0].replace("add ", "", 1).strip()
        file_name = parts[1].strip()

        if text_part and file_name:

            print(f"Adding: {text_part}")
            print(f"File: {file_name}")

            result = add_to_file(file_name, text_part)

            print(result)

            speak(result)

        else:

            speak("Please tell me what to add and which file to use.")

      except Exception as e:

        print("Add Error:", e)

        speak("Sorry, I couldn't add the text to the file.")
        # =====================================================
# READ TEXT FILE
# =====================================================

    elif "read " in command:

     file_name = command.replace("read ", "", 1).strip()

     if file_name:

        print(f"Reading file: {file_name}")

        content = read_file(file_name)

        if content:

            print("\nFile contents:")
            print(content)

            speak(content)

        else:

            speak(f"I couldn't find {file_name}.")

     else:

        speak("Please tell me which file you want me to read.")
   # =====================================================
# SEARCH FILES
# =====================================================

    elif "find " in command or "search for " in command:

     if "search for " in command:

        search_term = command.replace(
            "search for ", "", 1
        ).strip()

     else:

        search_term = command.replace(
            "find ", "", 1
        ).strip()

     if search_term:

        print(f"Searching for: {search_term}")

        results = search_files(search_term)

        if results:

            print("\nSearch Results:")

            for index, result in enumerate(results, start=1):

                print(f"{index}. {result}")

            count = len(results)

            if count == 1:

                speak(
                    f"I found one matching item "
                    f"for {search_term}."
                )

            else:

                speak(
                    f"I found {count} matching items "
                    f"for {search_term}."
                )

        else:

            print("No matching files or folders found.")

            speak(
                f"I couldn't find anything "
                f"matching {search_term}."
            )

     else:

        speak(
            "Please tell me what you want me to search for."
        )
    # =====================================================
    # OPEN LOCAL FILES AND FOLDERS
    # =====================================================
    
    elif "open " in command:
    
         name = command.replace("open ", "", 1).strip()
    
         if name:
    
            print(f"Looking for: {name}")
    
            result = open_file_or_folder(name)
    
            print(result)
    
            speak(result)
    
         else:
    
            speak("Please tell me what you want to open.")
    # =====================================================
    # OPEN WEBSITES
    # =====================================================
    elif command.startswith("open "):

        website = command.replace("open ", "").strip()

        websites = {
            "google": "https://www.google.com",
            "github": "https://github.com",
            "gmail": "https://mail.google.com",
            "chatgpt": "https://chat.openai.com",
            "facebook": "https://facebook.com",
            "instagram": "https://instagram.com",
            "linkedin": "https://linkedin.com",
            "wikipedia": "https://wikipedia.org",
            "amazon": "https://amazon.in",
            "flipkart": "https://flipkart.com"
        }

        if website in websites:

            speak(f"Opening {website}")
            webbrowser.open(websites[website])

        else:

            speak("Sorry, I don't know that website.")

    # =====================================================
    # PLAY SONGS
    # =====================================================
    elif command.startswith("play "):

        song = command.replace("play ", "").strip()

        speak(f"Playing {song}")

        webbrowser.open(
            "https://www.youtube.com/results?search_query=" +
            song.replace(" ", "+")
        )

    # =====================================================
    # GOOGLE SEARCH
    # =====================================================
    elif command.startswith("search "):

        query = command.replace("search ", "").strip()

        speak(f"Searching Google for {query}")

        webbrowser.open(
            "https://www.google.com/search?q=" +
            query.replace(" ", "+")
        )

    # =====================================================
    # TIME
    # =====================================================
    elif "time" in command:

        current_time = datetime.now().strftime("%I:%M %p")

        print(current_time)

        speak(f"The current time is {current_time}")

    # =====================================================
    # DATE
    # =====================================================
    elif "date" in command:

        current_date = datetime.now().strftime("%d %B %Y")

        print(current_date)

        speak(f"Today is {current_date}")

    # =====================================================
    # SCREENSHOT
    # =====================================================
    elif "screenshot" in command or "capture screen" in command:

        folder = "screenshots"

        os.makedirs(folder, exist_ok=True)

        filename = datetime.now().strftime("%Y-%m-%d_%H-%M-%S") + ".png"

        path = os.path.join(folder, filename)

        image = ImageGrab.grab()

        image.save(path)

        print("Saved:", path)

        speak("Screenshot taken successfully.")
   # =====================================================
# COMPUTER CONTROLS
# =====================================================

    elif (
     "lock computer" in command
     or "lock pc" in command
     or "lock laptop" in command
     or "lock my computer" in command
     or "lock my laptop" in command
):

     speak("Locking your computer")

     os.system(
        "rundll32.exe user32.dll,LockWorkStation"
    )


    elif (
     "restart computer" in command
     or "restart pc" in command
     or "restart laptop" in command
     or "restart my computer" in command
     or "restart my laptop" in command
):

     pending_system_action = "restart"
     pending_system_action_time = time.time()

     speak(
        "Are you sure you want to restart your computer?"
    )

     print(
        "Waiting for confirmation..."
    )

    elif (
     "shut down computer" in command
     or "shutdown computer" in command
     or "shutdown pc" in command
     or "shutdown laptop" in command
     or "shut down laptop" in command
     or "turn off computer" in command
     or "turn off laptop" in command
     or "turn off my computer" in command
     or "turn off my laptop" in command
     or "power off computer" in command
     or "power off laptop" in command
):

     pending_system_action = "shutdown"
     pending_system_action_time = time.time()

     speak(
        "Are you sure you want to shut down your computer?"
    )

     print(
        "Waiting for confirmation..."
    )


    elif (
     "sleep computer" in command
     or "sleep pc" in command
     or "sleep laptop" in command
     or "sleep my computer" in command
     or "sleep my laptop" in command
     or "put computer to sleep" in command
     or "put laptop to sleep" in command
):

     pending_system_action = "sleep"
     pending_system_action_time = time.time()

     speak(
        "Are you sure you want to put your computer to sleep?"
    )

     print(
        "Waiting for confirmation..."
    )

     return

    elif "log off" in command:

     speak("Logging off")

     os.system(
        "shutdown /l"
     )

    elif (
     "cancel shutdown" in command
     or "cancel restart" in command
     or "abort shutdown" in command
):

     os.system("shutdown /a")

     speak(
        "The scheduled shutdown or restart has been cancelled."
    )
    # =====================================================
    # WEATHER
    # =====================================================

    elif "weather" in command:

     print("Getting weather...")

     speak("Let me check the weather.")

     weather = get_weather("Bengaluru")

     print("Weather:", weather)

     speak(weather)
  # =====================================================
# VOLUME CONTROL
# =====================================================

    elif "increase volume" in command or "volume up" in command:

     increase_volume()

     current = get_volume()

     print(f"Volume: {current}%")

     speak(f"Volume increased to {current} percent.")


    elif "decrease volume" in command or "volume down" in command:

     decrease_volume()

     current = get_volume()

     print(f"Volume: {current}%")

     speak(f"Volume decreased to {current} percent.")


    elif "unmute volume" in command or command == "unmute":

     unmute_volume()

     print("Volume unmuted.")

     speak("Volume unmuted.")


    elif "mute volume" in command or command == "mute":

     mute_volume()

     print("Volume muted.")

     speak("Volume muted.")


    elif "set volume to" in command:

     try:

        words = command.split()
        percent = int(words[-1].replace("%", ""))

        set_volume(percent)

        print(f"Volume set to {percent}%")

        speak(f"Volume set to {percent} percent.")

     except Exception:

        speak("Please say a valid volume percentage.")
    # =====================================================
    # BRIGHTNESS CONTROL
    # =====================================================

    elif "increase brightness" in command or "brightness up" in command:

     increase_brightness()

     current = get_brightness()

     print(f"Brightness: {current}%")

     speak(f"Brightness increased to {current} percent.")


    elif "decrease brightness" in command or "brightness down" in command:

     decrease_brightness()

     current = get_brightness()

     print(f"Brightness: {current}%")

     speak(f"Brightness decreased to {current} percent.")


    elif "set brightness to" in command:

     try:

        words = command.split()
        percent = int(words[-1].replace("%", ""))

        set_brightness(percent)

        print(f"Brightness set to {percent}%")

        speak(f"Brightness set to {percent} percent.")

     except Exception:

        speak("Please say a valid brightness percentage.")
    # =====================================================
    # BATTERY STATUS
    # =====================================================

    elif matches_intent_groups(command, [
    ["battery", "charge", "charging"],
    ["status", "level", "percentage", "health"]
]):

     print("Checking battery...")

     speak("Let me check your battery.")

     battery_status = get_battery_status()

     print("Battery:", battery_status)

     speak(battery_status)
    
     # =====================================================
    # TOP CPU PROCESS
    # =====================================================
    
    elif (
         "which app is using the most cpu" in command
         or "which application is using the most cpu" in command
         or "what is using the most cpu" in command
         or "highest cpu usage" in command
    ):
    
         print("Checking top CPU process...")
    
         processes = get_top_cpu_processes(1)
    
         if processes:
    
            process = processes[0]
    
            name = process["name"]
            cpu = process["cpu"]
            pid = process["pid"]
    
            print(
                f"Top CPU Process: {name} "
                f"(PID {pid}) - {cpu}%"
            )
    
            speak(
                f"{name} is currently using "
                f"{cpu:.1f} percent CPU."
            )
    
         else:
    
            speak(
                "Sorry, I couldn't determine the top CPU process."
            )
        # =====================================================
# DETAILED SLOW SYSTEM DIAGNOSIS
# =====================================================

    elif (
        "why is my laptop slow" in command
        or "why is my computer slow" in command
        or "my laptop is slow" in command
        or "my computer is slow" in command
        or "diagnose my computer" in command
        or "diagnose my laptop" in command
        or "troubleshoot my laptop" in command
        or "troubleshoot my computer" in command
    ):

        print("Diagnosing system slowdown...")

        report = get_troubleshooting_report()

        print("Troubleshooting Report:", report)

        speak(report)
        # =====================================================
    # CPU HEALTH
    # =====================================================

    elif (
        "cpu health" in command
        or "is my cpu okay" in command
        or "is cpu okay" in command
        or "check cpu health" in command
        or "how is my cpu" in command
    ):

        print("Checking CPU health...")

        cpu_health = get_cpu_health()

        print("CPU Health:", cpu_health)

        speak(cpu_health)
 # =====================================================
# APPLICATION RESOURCE USAGE
# =====================================================

    elif matches_intent_groups(command, [
    ["application", "applications", "app", "apps"],
    ["resource", "resources", "cpu", "memory"],
    ["most", "highest", "using", "usage"]
]):
        print("APPLICATION RESOURCE COMMAND DETECTED")

        print("Checking application resource usage...")
     
        applications = get_application_resource_usage(5)

        if applications:

            print("Top Resource-Using Applications:")

            for app in applications:

                print(
                    f"{app['name']} "
                    f"(PID {app['pid']}) - "
                    f"CPU {app['cpu']:.1f}% - "
                    f"RAM {app['memory']:.1f}% - "
                    f"Score {app['resource_score']:.1f}"
                )

            # Get the highest resource-using application
            top = applications[0]

            severity = top["severity"]
            app_name = top["name"]

            # ---------------------------------------------
            # SEVERITY-BASED RECOMMENDATION
            # ---------------------------------------------

            if severity == "Very High":

                recommendation = (
                    f"{app_name} is using a very high amount "
                    f"of system resources and may be significantly "
                    f"affecting your computer's performance."
                )

            elif severity == "High":

                recommendation = (
                    f"{app_name} is using a high amount of resources. "
                    f"If you are not currently using it, "
                    f"consider closing it."
                )

            elif severity == "Moderate":

                recommendation = (
                    f"{app_name} is using a moderate amount of resources. "
                    f"You may want to keep an eye on it."
                )

            else:

                recommendation = (
                    f"{app_name} resource usage currently looks normal."
                )

            response = (
                f"The highest resource-using application is "
                f"{app_name}. "
                f"It is using {top['cpu']:.1f} percent CPU "
                f"and {top['memory']:.1f} percent memory. "
                f"Its resource score is "
                f"{top['resource_score']:.1f}, "
                f"which is classified as "
                f"{severity} resource usage. "
                f"{recommendation}"
            )

            speak(response)

        else:

            speak(
                "Sorry, I couldn't determine "
                "application resource usage."
            )
# =====================================================
# RESOURCE SPIKE DETECTION
# =====================================================

    elif matches_intent_groups(command, [
    ["spike", "spikes"],
    ["resource", "resources", "cpu", "memory"]
]):

        print("Checking for resource spikes...")

        spike = detect_resource_spike()

        if spike["spike_detected"]:

          print("\n===== RESOURCE SPIKE REPORT =====")
          print("Application:", spike["application"])
          print("Resource:", spike["resource"])
          print("Severity:", spike["severity"])
          print("Previous Usage:", spike["previous"], "%")
          print("Current Usage:", spike["current"], "%")
          print("Increase:", spike["increase"], "%")
          print("Recommendation:", spike["recommendation"])
          print("=================================\n")

        else:

         print("\n===== RESOURCE SPIKE REPORT =====")
         print("Status: No spike detected")
         print("Severity:", spike["severity"])
         print("Recommendation:", spike["recommendation"])
         print("=================================\n")

        speak(spike["message"])
# =====================================================
# REPEATED RESOURCE SPIKE DETECTION
# =====================================================

    elif matches_intent_groups(command, [
    ["repeated", "repeat", "keeps"],
    ["spike", "spikes", "spiking"]
]):

        print("Checking for repeated resource spikes...")

        result = detect_repeated_resource_spikes()

        print("\n===== REPEATED SPIKE REPORT =====")
        print(
            "Repeated Spike:",
            result["repeated_spike"]
        )
        print(
            "Application:",
            result["application"]
        )
        print(
            "Resource:",
            result["resource"]
        )
        print(
            "Spike Count:",
            result["spike_count"]
        )
        print(
            "Severity:",
            result.get("severity", "None")
        )
        print(
            "Recommendation:",
            result.get(
                "recommendation",
                "No action is required."
            )
        )
        print("=================================\n")

        speak(result["message"])
# =====================================================
# RESOURCE TREND DETECTION
# =====================================================

    elif matches_intent_groups(command, [
    ["trend", "trends", "increasing"],
    ["resource", "resources", "cpu", "memory"]
]):

        print("Checking application resource trends...")

        trend = detect_resource_trend()

        if trend["trend_detected"]:

            print("\n===== RESOURCE TREND REPORT =====")
            print("Trend Detected: True")
            print("Application:", trend["application"])
            print("Resource:", trend["resource"])
            print("Starting Usage:", trend["start"], "%")
            print("Current Usage:", trend["current"], "%")
            print("Increase:", trend["increase"], "%")
            print("Samples:", trend["samples"])
            print("Severity:", trend["severity"])
            print(
                "Recommendation:",
                trend["recommendation"]
            )
            print("=================================\n")

        else:

            print("\n===== RESOURCE TREND REPORT =====")
            print("Trend Detected: False")
            print("Samples Checked:", trend["samples"])
            print(
                "Severity:",
                trend.get("severity", "None")
            )
            print(
                "Recommendation:",
                trend.get(
                    "recommendation",
                    "No action is required."
                )
            )
            print("=================================\n")

        speak(trend["message"])
# =====================================================
# COMBINED RESOURCE INTELLIGENCE
# =====================================================
    elif matches_intent_groups(command, [
    ["system", "computer", "pc"],
    ["resource", "resources", "performance"]
]):
     print("Analyzing complete system resources...")
     report = get_combined_resource_intelligence()
     current = report.get("current", {})
     print("\n===== SYSTEM RESOURCE INTELLIGENCE =====")
     print("Top Application:", current.get("application"))
     print("CPU:", current.get("cpu", 0), "%")
     print("Memory:", current.get("memory", 0), "%")
     print("Resource Score:", current.get("resource_score", 0))
     print("Current Severity:", current.get("severity", "Unknown"))
     print("Latest Spike:", report.get("spike", {}).get("spike_detected", False))
     print("Repeated Spike:", report.get("repeated_spike", {}).get("repeated_spike", False))
     print("Trend Detected:", report.get("trend", {}).get("trend_detected", False))
     print("Overall Severity:", report.get("overall_severity", "Unknown"))
     print("========================================\n")
     speak(report["message"])
# =====================================================
# CPU USAGE
# =====================================================

    elif "cpu" in command:

     print("Checking CPU usage...")

     import psutil

     cpu_usage = psutil.cpu_percent(interval=1)

     response = f"Your CPU usage is {cpu_usage} percent."

     print("CPU:", response)

     speak(response)

    # =====================================================
# TOP MEMORY PROCESS
# =====================================================

    elif (
     "which app is using the most ram" in command
     or "which application is using the most ram" in command
     or "which app uses the most memory" in command
     or "which application uses the most memory" in command
     or "highest memory usage" in command
):

     print("Checking top memory process...")

     processes = get_top_memory_processes(1)

     if processes:

        process = processes[0]

        name = process["name"]
        memory = process["memory"]
        pid = process["pid"]

        print(
            f"Top Memory Process: {name} "
            f"(PID {pid}) - RAM {memory:.1f}%"
        )

        speak(
            f"{name} is currently using "
            f"{memory:.1f} percent of your memory."
        )

     else:

        speak(
            "Sorry, I couldn't determine the top memory process."
        )
        # =====================================================
    # RAM HEALTH
    # =====================================================

    elif (
        "ram health" in command
        or "memory health" in command
        or "is my ram okay" in command
        or "is my memory okay" in command
        or "check ram health" in command
        or "how is my ram" in command
    ):

        print("Checking RAM health...")

        ram_health = get_ram_health()

        print("RAM Health:", ram_health)

        speak(ram_health)
    # =====================================================
# RESOURCE HISTORY ANALYSIS
# =====================================================
    elif (
        "which application has been using the most memory" in command
        or "which applications has been using the most memory" in command
        or "which app has been using the most memory" in command
        or "which apps have been using the most memory" in command
        or "which application used the most memory" in command
        or "which app used the most memory" in command
        or "which application has used the most ram" in command
        or "which app has used the most ram" in command
    ):

        print("Analyzing resource history...")

        history = get_resource_history_analysis()

        application = history["application"]
        average_memory = history["average_memory"]
        average_cpu = history["average_cpu"]
        snapshots = history["snapshots"]

        if application:

            print("Application:", application)
            print("Average Memory:", average_memory)
            print("Average CPU:", average_cpu)
            print("Snapshots:", snapshots)

            response = (
                f"{application} has been using the most memory recently. "
                f"It averaged {average_memory:.1f} percent memory "
                f"across {snapshots} snapshots."
            )

            speak(response)

        else:

            speak(
                "I don't have enough resource history yet."
            )
    # =====================================================
# RAM / MEMORY USAGE
# =====================================================

    elif "ram" in command or "memory" in command:

     print("Checking RAM usage...")

     import psutil

     memory = psutil.virtual_memory()

     total = round(memory.total / (1024 ** 3), 1)
     used = round(memory.used / (1024 ** 3), 1)
     percent = round(memory.percent)

     response = (
        f"You have {total} gigabytes of RAM. "
        f"{used} gigabytes is currently being used, "
        f"which is {percent} percent."
    )

     print("RAM:", response)

     speak(response)
        # =====================================================
    # DISK HEALTH
    # =====================================================

    elif (
        "disk health" in command
        or "storage health" in command
        or "is my disk okay" in command
        or "is my storage okay" in command
        or "check disk health" in command
        or "how is my disk" in command
    ):

        print("Checking disk health...")

        disk_health = get_disk_health()

        print("Disk Health:", disk_health)

        speak(disk_health)
    # =====================================================
# DISK / STORAGE USAGE
# =====================================================

    elif "disk" in command or "storage" in command:

     print("Checking disk usage...")

     import psutil

     disk = psutil.disk_usage("C:\\")

     total = round(disk.total / (1024 ** 3), 1)
     used = round(disk.used / (1024 ** 3), 1)
     free = round(disk.free / (1024 ** 3), 1)
     percent = round(disk.percent)

     response = (
        f"Your C drive has {total} gigabytes total. "
        f"{used} gigabytes is used and "
        f"{free} gigabytes is free. "
        f"That is {percent} percent used."
    )

     print("Storage:", response)

     speak(response)

    # =====================================================
# QUICK SYSTEM STATUS
# =====================================================

    elif (
     "quick system status" in command
     or "quick status" in command
     or "give me a quick status" in command
):

     print("Checking quick system status...")

     status = get_short_system_info()

     print("Quick Status:", status)

     speak(status)
    # =====================================================
# RUNNING USER APPLICATIONS
# =====================================================

    elif (
        "what applications are running" in command
        or "what apps are running" in command
        or "which applications are running" in command
        or "which apps are running" in command
        or "show running applications" in command
    ):

        print("Checking running applications...")

        applications = get_running_applications()

        if applications:

            # Show only first 10 applications
            top_applications = applications[:10]

            app_text = ", ".join(
                app["name"]
                for app in top_applications
            )

            print("Running Applications:")
            print(app_text)

            speak(
                f"I found {len(applications)} running applications. "
                f"Some of them are {app_text}"
            )

        else:

            speak(
                "Sorry, I couldn't find any running applications."
            )

    # =====================================================
# RUNNING PROCESSES
# =====================================================

    elif (
     "show running processes" in command
     or "show running process" in command
     or "what processes are running" in command
     or "show running apps" in command
     
):

     print("Checking running processes...")

     processes = get_running_processes()

     if processes:

        # Show only first 10 processes
        top_processes = processes[:10]

        process_text = ", ".join(
            top_processes
        )

        print("Running Processes:")
        print(process_text)

        speak(
            f"I found {len(processes)} running processes. "
            f"Some of them are {process_text}"
        )
 
     else:

        speak(
            "Sorry, I couldn't get the running processes."
        )
        # =====================================================
    # DETAILED SYSTEM HEALTH
    # =====================================================

    elif (
        "detailed system health" in command
        or "detailed health report" in command
        or "full system health" in command
        or "complete system health" in command
        or "system health report" in command
    ):

        print("Generating detailed system health report...")

        report = get_detailed_system_health()

        print("Detailed System Health:", report)

        speak(report)

    # =====================================================
# SYSTEM HEALTH
# =====================================================

    elif matches_intent_groups(command, [
    ["system", "computer", "pc"],
    ["health", "status", "condition"]
]):

     print("Checking system health...")

     health = get_system_health()

     print("System Health:", health)

     speak(health)
    # =====================================================
# SYSTEM INFORMATION
# =====================================================

    elif (
     "system status" in command
     or "system information" in command
     or "computer status" in command
     or "pc status" in command
     or "system details" in command
     or "computer information" in command
     or "tell me about my laptop" in command
):

     print("Checking system status...")

     speak("Let me check your system status.")

     system_status = get_system_info()

     print("System:", system_status)

     speak(system_status)
    # =====================================================
# FILE AND FOLDER CREATION
# =====================================================

    elif "create a folder called" in command:

     folder_name = command.split("create a folder called", 1)[1].strip()

     if folder_name:

        print(f"Creating folder: {folder_name}")

        result = create_folder(folder_name)

        print(result)

        speak(result)

     else:

        speak("Please tell me the folder name.")


    elif "create folder called" in command:

     folder_name = command.split("create folder called", 1)[1].strip()

     if folder_name:

        print(f"Creating folder: {folder_name}")

        result = create_folder(folder_name)

        print(result)

        speak(result)

     else:

        speak("Please tell me the folder name.")


    elif "create a text file called" in command:

     file_name = command.split("create a text file called", 1)[1].strip()

     if file_name:

        print(f"Creating text file: {file_name}")

        result = create_text_file(file_name)

        print(result)

        speak(result)

     else:

        speak("Please tell me the file name.")


    elif "create text file called" in command:

     file_name = command.split("create text file called", 1)[1].strip()

     if file_name:

        print(f"Creating text file: {file_name}")

        result = create_text_file(file_name)

        print(result)

        speak(result)

     else:

        speak("Please tell me the file name.")
    # =====================================================
# DELETE FILE OR FOLDER - WITH CONFIRMATION
# =====================================================

    elif "delete " in command:

     item_name = command.replace("delete ", "", 1).strip()

     if not item_name:

        speak("Please tell me what you want to delete.")
        return

     print(f"Delete request: {item_name}")

     speak(
        f"Are you sure you want to delete {item_name}? "
        "Please say yes or no."
     )

     confirmation = input(
        "Type YES to confirm deletion or NO to cancel: "
     ).strip().lower()

     if confirmation == "yes":

        result = delete_file_or_folder(item_name)

        print(result)

        speak(result)

     else:

        print("Deletion cancelled.")

        speak("Deletion cancelled.")

  # =====================================================
# CLOSE APPLICATION
# =====================================================

    elif command.startswith("close "):

     app_command = command.replace(
        "close ", "", 1
     ).strip()

     smart_app = find_application_alias(
        app_command
     )

     if smart_app == "chrome":

        app_name = "chrome"

     elif smart_app == "edge":

        app_name = "msedge"

     elif smart_app == "vscode":

        app_name = "code"

     elif smart_app == "notepad":

        app_name = "notepad"

     elif smart_app == "calculator":

        app_name = "calculator"

     elif smart_app == "paint":

        app_name = "mspaint"

     elif smart_app == "explorer":

        app_name = "explorer"

     else:

        app_name = app_command

     print(
        f"Closing application: {app_name}"
     )

     result = close_application(app_name)

     print(result)

     speak(result)
   
    # =====================================================
    # AI CHAT
    # =====================================================
    else:

         print("Thinking...")

         speak("Let me think.")

         reply = ask_ai(command)

         print("\nAI:\n")
         print(reply)

         # Speak only the first sentence
         first_sentence = reply.split(".")[0].strip() + "."

         first_sentence = re.sub(r"[^\x20-\x7E]", " ", first_sentence)
         first_sentence = " ".join(first_sentence.split())

         speak(first_sentence)