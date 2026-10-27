import os
import subprocess


APPS = {
    "notepad": "notepad.exe",
    "calculator": "calc.exe",
    "paint": "mspaint.exe",
    "command prompt": "cmd.exe",
    "cmd": "cmd.exe",
    "powershell": "powershell.exe",
}


def open_app(app_name):

    app_name = app_name.lower().strip()

    if app_name in APPS:

        try:

            subprocess.Popen(APPS[app_name])

            return f"Opening {app_name}."

        except Exception as e:

            print("Application Error:", e)

            return f"I couldn't open {app_name}."

    return None