🤖 SAM AI Desktop Assistant

SAM AI Desktop is an intelligent, voice-activated desktop assistant built in Python. It combines biometric facial recognition, local Large Language Model (LLM) capabilities via Ollama, and comprehensive system automation to give you hands-free control over your PC.

✨ Features

🔐 Biometric Face Unlock (desktop_face.py): Securely authenticates the user via facial recognition before granting access to the assistant.

🧠 Local AI Chat (ollama_chat.py): Powered by Ollama for intelligent, privacy-focused offline/local conversational AI.

🎙️ Voice Interaction (voice.py): Seamless Speech-to-Text (STT) and Text-to-Speech (TTS) for natural hands-free communication.

💻 Desktop & System Control (desktop_control.py, actions.py): Automate routine desktop tasks, window management, and custom workflows.

🚀 Application Launcher (apps.py): Open and manage desktop applications using simple voice commands.

📁 Smart File Manager (file_manager.py): Search, organize, create, and manage files and directories effortlessly.

⚙️ Hardware & System Monitoring:

System Info (system_info.py): Real-time CPU, RAM, and OS diagnostics.

Battery Monitor (battery.py): Check battery percentage and power status.

Volume & Brightness (volume.py, brightness.py): Adjust system audio levels and screen brightness on the fly.

🌦️ Live Weather Updates (weather.py): Fetch real-time weather forecasts and conditions.

⚡ Background Worker & Startup (desktop_worker.py, startup.py): Multi-threaded background execution and system startup integration.

📂 Project Structure

SAM_AI_Desktop/
│
├── database/                   # Stores local user profiles (e.g., face_profile.pkl)
├── modules/                    # Core assistant capabilities
│   ├── __init__.py
│   ├── actions.py              # Command routing and action execution
│   ├── apps.py                 # Application launching utilities
│   ├── battery.py              # Battery status monitoring
│   ├── brightness.py           # Screen brightness control
│   ├── desktop_control.py      # OS-level window and desktop automation
│   ├── file_manager.py         # File and directory operations
│   ├── ollama_chat.py          # Local LLM integration via Ollama
│   ├── system_info.py          # System hardware/software telemetry
│   ├── voice.py                # Speech recognition & synthesis
│   ├── volume.py               # Master volume control
│   └── weather.py              # Weather API integration
│
├── desktop_face.py             # Facial recognition authentication module
├── desktop_worker.py           # Background thread worker for smooth execution
├── main.py                     # Primary entry point for SAM AI Desktop
├── startup.py                  # Initialization and startup routines
├── requirements.txt            # Python dependencies
└── START_HERE.txt              # Quick-start instructions


🛠️ Prerequisites

Python 3.10+ (Developed and tested on Python 3.12)

Ollama: Installed locally for AI chat features.

Download from ollama.com

Pull your preferred model in the terminal (e.g., ollama run llama3 or ollama run mistral).

Webcam & Microphone: Required for facial authentication and voice commands.

🚀 Installation & Setup

Clone the repository:

git clone https://github.com/YOUR_USERNAME/SAM-AI-Desktop.git
cd SAM-AI-Desktop


Create a virtual environment (recommended):

python -m venv venv
# On Windows:
venv\Scripts\activate
# On macOS/Linux:
source venv/bin/activate


Install required dependencies:

pip install -r requirements.txt


Set up your Face Profile (First Run):
Ensure the database/ folder exists. On your first run, configure or register your face profile using desktop_face.py if prompted.

Run the Assistant:

python main.py


🗣️ Example Commands

"Open Chrome / Notepad / Calculator"

"What is my battery percentage?"

"Set brightness to 80 percent"

"Mute the volume" / "Increase volume"

"What's the weather like today?"

"Check system CPU and RAM usage"

"Create a new folder in Documents"

Ask general knowledge or coding questions (handled via Ollama)

🤝 Contributing

Contributions, issues, and feature requests are welcome! Feel free to fork the repository and submit a pull request.

📄 License

This project is open-source and available under the MIT License.
