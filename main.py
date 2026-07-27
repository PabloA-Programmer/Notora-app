import customtkinter as ctk
from tkinter import filedialog, messagebox
from openai import OpenAI
import os
import threading
import json
from pydub import AudioSegment
import time
from PIL import Image
import sys
import os

# Resolves the correct path for resources (images, ffmpeg, etc.)
# Handles both regular Python execution and PyInstaller bundled executables.
def resource_path(relative_path):
    try:
        # PyInstaller's temporary folder path
        base_path = sys._MEIPASS
    except Exception:
        # Regular Python execution - current directory
        base_path = os.path.abspath("")

    return os.path.join(base_path, relative_path)

# Configure pydub to use the bundled ffmpeg executable for audio conversion
AudioSegment.converter = resource_path("ffmpeg/ffmpeg.exe")


# Main application class for transcription and note generation
class TranscriptorApp(ctk.CTk):
    def __init__(self):
        super().__init__()

        # Initialize configuration file and load API key from settings
        self.config_file = "settings.json"
        self.api_key = self.cargar_config()

        # ======================
        # WINDOW CONFIG (PREMIUM)
        # ======================
        # Set dark theme with blue accent color for modern appearance
        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("blue")

        # Configure main window properties
        self.title("NOTORA")
        self.geometry("800x900")
        self.minsize(750, 850)

        # Set window icon (skip if not found)
        try:
            self.iconbitmap(resource_path("logo.ico"))
        except:
            pass

        # ======================
        # MAIN CONTAINER
        # ======================
        # Create transparent main frame that holds all content
        main = ctk.CTkFrame(self, fg_color="transparent")
        main.pack(fill="both", expand=True, padx=30, pady=25)

        # ======================
        # HEADER (MINIMAL PREMIUM)
        # ======================
        # Create header container for logo and title
        header = ctk.CTkFrame(main, fg_color="transparent")
        header.pack(pady=(10, 25))

        # Load and display logo image
        try:
            logo = ctk.CTkImage(
                light_image=Image.open(resource_path("logo.ico")),
                dark_image=Image.open(resource_path("logo.ico")),
                size=(70, 70)
            )

            ctk.CTkLabel(header, image=logo, text="").pack()

        except:
            pass

        # Display application title
        ctk.CTkLabel(
            header,
            text="NOTORA",
            font=("Arial", 34, "bold")
        ).pack()

        # Display subtitle describing the application
        ctk.CTkLabel(
            header,
            text="AI-powered transcription & study assistant",
            font=("Arial", 14),
            text_color="gray"
        ).pack()

        # ======================
        # CARD (PREMIUM PANEL)
        # ======================
        # Create main content card with rounded corners
        card = ctk.CTkFrame(
            main,
            corner_radius=20,
            fg_color="#1e1e1e"
        )
        card.pack(fill="both", expand=True)

        # ======================
        # FILE SECTION
        # ======================
        # Display "Input file" label
        ctk.CTkLabel(card, text="Input file", font=("Arial", 14, "bold")).pack(pady=(20, 5))

        # Button to open file dialog for selecting audio or video files
        ctk.CTkButton(
            card,
            text="Select audio or video file",
            height=40,
            command=self.seleccionar_archivo
        ).pack(pady=5)

        # Label to display the name of selected file
        self.lbl_archivo = ctk.CTkLabel(card, text="No file selected", text_color="gray")
        self.lbl_archivo.pack(pady=(0, 15))

        # ======================
        # MODE SECTION
        # ======================
        # Display "Processing mode" label
        ctk.CTkLabel(card, text="Processing mode", font=("Arial", 14, "bold")).pack(pady=(10, 5))

        # Dropdown menu for selecting processing mode
        self.modo = ctk.CTkOptionMenu(
            card,
            values=[
                "Full Notes",
                "Quick Summary",
                "Examination Mode"
            ],
            width=250
        )
        self.modo.pack(pady=10)

        # ======================
        # ACTION BUTTON
        # ======================
        # Main button to start transcription and note generation process
        self.btn_run = ctk.CTkButton(
            card,
            text="Generate AI Notes",
            height=45,
            fg_color="#2563eb",
            hover_color="#1d4ed8",
            font=("Arial", 14, "bold"),
            command=self.iniciar_hilo
        )
        self.btn_run.pack(pady=15)

        # ======================
        # PROGRESS
        # ======================
        # Progress bar to show processing status
        self.progress_bar = ctk.CTkProgressBar(card, width=500)
        self.progress_bar.pack(pady=(5, 15))
        self.progress_bar.set(0)

        # ======================
        # OUTPUT (PREMIUM PANEL)
        # ======================
        # Display "Output" label
        ctk.CTkLabel(card, text="Output", font=("Arial", 14, "bold")).pack(pady=(10, 5))

        # Text box to display generated notes and processing messages
        self.output_text = ctk.CTkTextbox(
            card,
            width=650,
            height=300,
            corner_radius=12
        )
        self.output_text.pack(pady=(0, 20))

        # STATE
        # Variable to store the path of selected audio/video file
        self.archivo_ruta = ""

    # ======================
    # CONFIG
    # ======================
    # Load API key from the configuration file (settings.json)
    def cargar_config(self):
        if os.path.exists(self.config_file):
            try:
                with open(self.config_file, "r") as f:
                    return json.load(f).get("api_key", "")
            except:
                return ""
        return ""

    # Display dialog to request and save OpenAI API key
    def pedir_api_key(self):
        dialog = ctk.CTkInputDialog(text="Enter your API Key", title="API Key")
        key = dialog.get_input()

        if key:
            with open(self.config_file, "w") as f:
                json.dump({"api_key": key}, f)
            self.api_key = key

    # ======================
    # SAFE UI
    # ======================
    # Execute UI updates safely from worker threads using Tkinter's after() method
    def safe_ui(self, func, *args):
        self.after(0, lambda: func(*args))

    # ======================
    # FILE
    # ======================
    # Open file dialog to select an audio or video file
    def seleccionar_archivo(self):
        self.archivo_ruta = filedialog.askopenfilename(
            filetypes=[("Audio/Video", "*.mp3 *.wav *.m4a *.mp4")]
        )
        if self.archivo_ruta:
            # Display only the filename (not the full path)
            self.lbl_archivo.configure(text=os.path.basename(self.archivo_ruta))

    # ======================
    # THREAD
    # ======================
    # Start transcription and note generation process in a background thread
    def iniciar_hilo(self):
        # Check if API key is configured, request it if not
        if not self.api_key:
            self.pedir_api_key()
            return

        # Check if a file has been selected
        if not self.archivo_ruta:
            messagebox.showwarning("Error", "Choose a file")
            return

        # Disable the run button to prevent multiple concurrent submissions
        self.btn_run.configure(state="disabled")
        # Start processing in a background daemon thread
        threading.Thread(target=self.ejecutar, daemon=True).start()

    # ======================
    # PROMPTS
    # ======================
    # Generate the appropriate prompt for GPT based on the selected processing mode
    def obtener_prompt(self, modo, texto):
        modo_lower = modo.lower()

        # Mode 1: Comprehensive structured study notes
        if "full notes" in modo_lower:
            return f"""
Convert into structured study notes in English.
- clear topics
- bullet points
- simple explanations
- final summary

Text:
{texto}
"""

        # Mode 2: Brief summary (maximum 10 lines)
        elif "quick summary" in modo_lower:
            return f"""
Summarize in max 10 lines.
Only key ideas.

Text:
{texto}
"""

        # Mode 3: Exam preparation (questions and answers)
        elif "examination mode" in modo_lower:
            return f"""
Create exam questions + answers.
Highlight key concepts.

Text:
{texto}
"""

        # Fallback: return original text if mode doesn't match
        return texto

    # ======================
    # MAIN PROCESS
    # ======================
    # Main execution function for transcription and note generation workflow
    def ejecutar(self):
        # Initialize OpenAI client with API key
        client = OpenAI(api_key=self.api_key)
        ruta = self.archivo_ruta
        temp_file = None  # Placeholder for temporary compressed file

        try:
            # Update progress bar and clear output text box
            self.safe_ui(self.progress_bar.set, 0.1)
            self.safe_ui(self.output_text.delete, "1.0", "end")

            # Get file size in megabytes
            size_mb = os.path.getsize(ruta) / (1024 * 1024)

            # Compress audio if file is larger than 25MB to reduce API costs and time
            if size_mb > 25:
                self.safe_ui(self.output_text.insert, "end", "Compressing audio...\n")
                audio = AudioSegment.from_file(ruta)
                # Create temporary compressed file with timestamp in name
                temp_file = f"temp_{int(time.time())}.mp3"
                # Export with reduced bitrate for compression
                audio.export(temp_file, format="mp3", bitrate="96k")
                ruta = temp_file

            self.safe_ui(self.progress_bar.set, 0.3)

            # Display transcription status
            self.safe_ui(self.output_text.insert, "end", "Transcribing...\n")

            # Send audio file to Whisper API for transcription
            with open(ruta, "rb") as f:
                transcription = client.audio.transcriptions.create(
                    model="whisper-1",
                    file=f
                )

            # Extract transcribed text from the response
            texto = transcription.text

            self.safe_ui(self.progress_bar.set, 0.7)

            # Get selected processing mode
            modo = self.modo.get()
            # Generate appropriate prompt based on the selected mode
            prompt = self.obtener_prompt(modo, texto)

            # Display AI processing status
            self.safe_ui(self.output_text.insert, "end", "Generating AI output...\n")

            # Send transcribed text and prompt to GPT-4 for processing
            response = client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {"role": "system", "content": "You are an expert study assistant."},
                    {"role": "user", "content": prompt}
                ]
            )

            # Extract the generated content from the response
            resultado = response.choices[0].message.content

            self.safe_ui(self.progress_bar.set, 0.9)

            # Create output directory if it doesn't exist
            os.makedirs("output", exist_ok=True)
            # Generate filename with timestamp to avoid overwrites
            filename = f"output/Notes_{int(time.time())}.txt"

            # Write generated notes to output file
            with open(filename, "w", encoding="utf-8") as f:
                f.write(resultado)

            # Display success message and mark completion
            self.safe_ui(self.output_text.insert, "end", f"\nSaved: {filename}")
            self.safe_ui(self.progress_bar.set, 1.0)

        except Exception as e:
            # Display error message to user if any exception occurs
            self.safe_ui(messagebox.showerror, "Error", str(e))

        finally:
            # Delete temporary compressed file if it was created
            if temp_file and os.path.exists(temp_file):
                os.remove(temp_file)

            # Re-enable the run button for next submission
            self.safe_ui(self.btn_run.configure, {"state": "normal"})


if __name__ == "__main__":
    # Create and run the main application
    app = TranscriptorApp()
    app.mainloop()
