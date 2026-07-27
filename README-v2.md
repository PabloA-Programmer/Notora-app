# 🎙️ NOTORA — AI-Powered Transcription & Study Assistant

![Python Version](https://img.shields.io/badge/python-3.8%2B-blue.svg)
![License](https://img.shields.io/badge/license-MIT-green.svg)
![UI](https://img.shields.io/badge/GUI-CustomTkinter-darkblue.svg)
![AI](https://img.shields.io/badge/AI-OpenAI%20Whisper%20%2B%20GPT--4o--mini-orange.svg)

**NOTORA** is a modern, intuitive cross-platform desktop application built with **CustomTkinter** and powered by **OpenAI** technologies (`whisper-1` and `gpt-4o-mini`). It automatically converts any audio or video file into structured study notes, quick executive summaries, or exam preparation practice questions.

---

## 📑 Table of Contents

- [✨ Key Features](#-key-features)
- [💻 User Interface](#-user-interface)
- [⚙️ System Requirements](#️-system-requirements)
- [🚀 Installation & Setup](#-installation--setup)
- [📂 Project Structure](#-project-structure)
- [🎯 How to Use](#-how-to-use)
- [🧩 Technical Highlights](#-technical-highlights)
- [📄 License](#-license)

---

## ✨ Key Features

- 🎨 **Modern Dark UI**: Elegant and clean dark-mode interface powered by CustomTkinter.
- 🎙️ **High-Accuracy Transcription**: Leverages OpenAI's `whisper-1` model to speech-to-text audio with exceptional accuracy.
- 🗜️ **Automatic File Compression (>25MB)**: If an audio/video file exceeds OpenAI's 25 MB size limit, NOTORA automatically compresses it using `pydub` and `FFmpeg`.
- 🧠 **Three AI Processing Modes**:
  - **Full Notes**: Generates complete, structured study material categorized by topics with clear bullet points, simple explanations, and a final summary.
  - **Quick Summary**: Condenses the entire recording into a high-level executive summary in under 10 lines.
  - **Examination Mode**: Creates a comprehensive question & answer bank tailored for self-testing key concepts.
- ⚡ **Asynchronous Threading**: The graphical interface remains smooth and non-blocking while processing large media files and AI requests.
- 💾 **Auto-Saving & Output Management**: Automatically exports generated notes to plain text (`.txt`) files inside the `/output` folder.

---

## 💻 User Interface

Designed with a sleek, user-friendly dark theme:

- **Header Section**: App title and branding logo.
- **Input File Section**: Easy selection of audio/video files (`.mp3`, `.wav`, `.m4a`, `.mp4`).
- **Mode Dropdown**: Seamless switching between AI study prompts.
- **Dynamic Progress Bar**: Real-time visual feedback for audio compression, transcription, and AI generation stages.
- **Output Area**: Integrated scrollable text preview for real-time results display.

---

## ⚙️ System Requirements

- **Python**: v3.8 or higher.
- **FFmpeg**: Required for audio manipulation and compression via `pydub`.
- **OpenAI API Key**: An active OpenAI account with API usage credits.

---

## 🚀 Installation & Setup

### 1. Clone the Repository

```bash
git clone https://github.com/your-username/notora.git
cd notora
```

### 2. Install Python Dependencies

Install all necessary Python packages:

```bash
pip install customtkinter openai pydub pillow
```

### 3. Setup FFmpeg

The application includes built-in support for local FFmpeg executable paths.

1. Download the **FFmpeg** executable for your OS from [ffmpeg.org](https://ffmpeg.org/).
2. Create a folder named `ffmpeg` in the root directory of the project.
3. Place the `ffmpeg.exe` binary inside that folder:
   ```text
   notora/
   ├── ffmpeg/
   │   └── ffmpeg.exe
   ├── logo.ico
   └── main.py
   ```

---

## 📂 Project Structure

```text
notora/
├── ffmpeg/
│   └── ffmpeg.exe          # Local FFmpeg executable for compression
├── output/                 # Automatically created directory for exported .txt notes
├── logo.ico                # App window icon & logo
├── settings.json           # Stores local API configuration (generated on first run)
├── main.py                 # Main application source code
└── README.md               # Project documentation
```

---

## 🎯 How to Use

1. **Run the Application**:
   ```bash
   python main.py
   ```
2. **Set Your API Key**: On the first execution (or if missing), a prompt window will ask for your OpenAI API Key. It will be stored locally in `settings.json`.
3. **Select Media File**: Click **"Select audio or video file"** to choose your input (`.mp3`, `.wav`, `.m4a`, `.mp4`).
4. **Choose Processing Mode**:
   - `Full Notes` for structured learning and detailed study guides.
   - `Quick Summary` for rapid overviews.
   - `Examination Mode` for practice questions.
5. **Generate AI Notes**: Click **"Generate AI Notes"**. The progress bar will indicate status updates, and the final output will be saved inside `output/`.

---

## 🧩 Technical Highlights

- **Config Persistence**: Automatic management of `settings.json` so you only enter your API Key once.
- **PyInstaller Compatibility**: Implements `resource_path()` for seamless binary bundling into a standalone `.exe` using PyInstaller.
- **Thread-Safe UI Operations**: Threading combined with Tkinter's `.after()` scheduling (`safe_ui`) guarantees UI responsiveness without thread crashes.

---

## 📄 License

This project is licensed under the **MIT License**. See the `LICENSE` file for full details.
