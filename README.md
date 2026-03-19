# JarvisAI

JarvisAI is a Python-based personal voice assistant with a modern Qt5 glassmorphism interface. Designed to streamline your daily tasks, Jarvis uses speech recognition to understand your voice commands and the high-fidelity ElevenLabs API to respond naturally.

## Features

- **Voice Interaction:** Speak naturally to Jarvis. Responses are generated with high-quality Text-to-Speech (TTS) via ElevenLabs.
- **System Integration:** Open standard applications (Notepad, Command Prompt, Discord, Camera, Calculator, etc.) via voice.
- **Web Capabilities:** Perform web searches, fetch live news, check live weather, and play YouTube videos.
- **School Mode API:** Integration with Google APIs to check emails and Classroom assignments (requires `credentials.json`).
- **Dynamic UI:** A seamless PyQt5-based graphical interface featuring a central glowing interaction status and conversational chat log.

## Prerequisites

Before running JarvisAI, you need a few core components installed and set up locally:

- Python 3.8+ (macOS/Windows/Linux)
- [ElevenLabs](https://elevenlabs.io/) API Key for Voice Generation
- Microphone access
- *Optional:* Google Cloud Console `credentials.json` if using the "School Mode" functionality for checking emails/assignments.

## Installation

1. **Clone the Repository**
   ```bash
   git clone https://github.com/your-username/JarvisAI.git
   cd JarvisAI
   ```

2. **Set up a Virtual Environment (Recommended)**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows use `venv\Scripts\activate`
   ```

3. **Install Dependencies**
   It's recommended to install dependencies via `pip`:
   ```bash
   pip install -r requirements.txt
   ```
   *Note on SpeechRecognition: You might need to install `pyaudio` specifically for your OS if a standard pip install fails (e.g., `brew install portaudio` followed by `pip install pyaudio` on macOS).*

## Configuration

JarvisAI uses environment variables for secure authentication. 

1. Copy `.env.example` to a new `.env` file:
   ```bash
   cp .env.example .env
   ```

2. Edit `.env` with your information and keys:
   ```env
   USER=YourName
   BOTNAME=Jarvis
   ELEVENLABS_API_KEY=your_elevenlabs_api_key_here
   ```

3. **Google API Credentials** (Optional, for School Mode): 
   Place your `credentials.json` file in the root of the project directory.

## Usage

Simply run the main Python script to launch the UI:

```bash
python main.py
```

Once the UI launches, press the **Wake Jarvis** button or say "Hey Jarvis" to begin interacting!

## Future Enhancements
- Expanded automation integrations
- Support for more open-source TTS models

## License

Please see the [LICENSE](LICENSE) file for more information.
