# Whisper Tranny
Whisper Tranny is a lightweight tool that records audio from your microphone and transcribes it using OpenAI’s open source Whisper speech-to-text model.

# Getting Started
This Python application is designed to run on Windows, macOS, and Linux.
At the time of writing, it has only been tested on Linux. The other operating systems are supported as far as currently known, but feedback from Windows and macOS users is very welcome.

# Setup
## Create a virtual environment (recommended)
python -m venv venv

## Activate the virtual environment

### Linux / macOS
source venv/bin/activate

### Windows (Command Prompt)
venv\Scripts\activate.bat

### Windows (PowerShell)
venv\Scripts\Activate.ps1

## Install dependencies
pip install -r requirements.txt

## Start the application
On first launch, the small model will download approximately 1–2 GB of data.

### Linux / macOS
./start.sh

### Windows
./start.bat

# Features
* Cross-platform – Runs on Linux, Windows, and macOS
* One-click recording – Green button starts recording, red button stops it
* Visual feedback – Status label shows the current state
* Background transcription – The UI stays responsive while Whisper is processing
* Easy text copying – “Copy all” button or select text and press Ctrl + C
* German language support – Whisper is configured for German by default

# Configuration
You can change the Whisper model by editing the line with model_name="base":
- tiny – Fastest, lowest accuracy
- base – Good overall balance
- small – Better accuracy for German
- medium – Higher accuracy
- large – Best quality, GPU recommended
