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

def resource_path(relative_path):
    try:
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath("")

    return os.path.join(base_path, relative_path)

AudioSegment.converter = resource_path("ffmpeg/ffmpeg.exe")


class TranscriptorApp(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.config_file = "settings.json"
        self.api_key = self.cargar_config()

        # ======================
        # WINDOW CONFIG (PREMIUM)
        # ======================
        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("blue")

        self.title("NOTORA")
        self.geometry("800x900")
        self.minsize(750, 850)

        try:
            self.iconbitmap(resource_path("logo.ico"))
        except:
            pass

        # ======================
        # MAIN CONTAINER
        # ======================
        main = ctk.CTkFrame(self, fg_color="transparent")
        main.pack(fill="both", expand=True, padx=30, pady=25)

        # ======================
        # HEADER (MINIMAL PREMIUM)
        # ======================
        header = ctk.CTkFrame(main, fg_color="transparent")
        header.pack(pady=(10, 25))

        try:
            logo = ctk.CTkImage(
                light_image=Image.open(resource_path("logo.ico")),
                dark_image=Image.open(resource_path("logo.ico")),
                size=(70, 70)
            )

            ctk.CTkLabel(header, image=logo, text="").pack()

        except:
            pass

        ctk.CTkLabel(
            header,
            text="NOTORA",
            font=("Arial", 34, "bold")
        ).pack()

        ctk.CTkLabel(
            header,
            text="AI-powered transcription & study assistant",
            font=("Arial", 14),
            text_color="gray"
        ).pack()

        # ======================
        # CARD (PREMIUM PANEL)
        # ======================
        card = ctk.CTkFrame(
            main,
            corner_radius=20,
            fg_color="#1e1e1e"
        )
        card.pack(fill="both", expand=True)

        # ======================
        # FILE SECTION
        # ======================
        ctk.CTkLabel(card, text="Input file", font=("Arial", 14, "bold")).pack(pady=(20, 5))

        ctk.CTkButton(
            card,
            text="Select audio or video file",
            height=40,
            command=self.seleccionar_archivo
        ).pack(pady=5)

        self.lbl_archivo = ctk.CTkLabel(card, text="No file selected", text_color="gray")
        self.lbl_archivo.pack(pady=(0, 15))

        # ======================
        # MODE SECTION
        # ======================
        ctk.CTkLabel(card, text="Processing mode", font=("Arial", 14, "bold")).pack(pady=(10, 5))

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
        self.progress_bar = ctk.CTkProgressBar(card, width=500)
        self.progress_bar.pack(pady=(5, 15))
        self.progress_bar.set(0)

        # ======================
        # OUTPUT (PREMIUM PANEL)
        # ======================
        ctk.CTkLabel(card, text="Output", font=("Arial", 14, "bold")).pack(pady=(10, 5))

        self.output_text = ctk.CTkTextbox(
            card,
            width=650,
            height=300,
            corner_radius=12
        )
        self.output_text.pack(pady=(0, 20))

        # STATE
        self.archivo_ruta = ""

    # ======================
    # CONFIG
    # ======================
    def cargar_config(self):
        if os.path.exists(self.config_file):
            try:
                with open(self.config_file, "r") as f:
                    return json.load(f).get("api_key", "")
            except:
                return ""
        return ""

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
    def safe_ui(self, func, *args):
        self.after(0, lambda: func(*args))

    # ======================
    # FILE
    # ======================
    def seleccionar_archivo(self):
        self.archivo_ruta = filedialog.askopenfilename(
            filetypes=[("Audio/Video", "*.mp3 *.wav *.m4a *.mp4")]
        )
        if self.archivo_ruta:
            self.lbl_archivo.configure(text=os.path.basename(self.archivo_ruta))

    # ======================
    # THREAD
    # ======================
    def iniciar_hilo(self):
        if not self.api_key:
            self.pedir_api_key()
            return

        if not self.archivo_ruta:
            messagebox.showwarning("Error", "Choose a file")
            return

        self.btn_run.configure(state="disabled")
        threading.Thread(target=self.ejecutar, daemon=True).start()

    # ======================
    # PROMPTS
    # ======================
    def obtener_prompt(self, modo, texto):
        modo_lower = modo.lower()

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

        elif "quick summary" in modo_lower:
            return f"""
Summarize in max 10 lines.
Only key ideas.

Text:
{texto}
"""

        elif "examination mode" in modo_lower:
            return f"""
Create exam questions + answers.
Highlight key concepts.

Text:
{texto}
"""

        return texto

    # ======================
    # MAIN PROCESS
    # ======================
    def ejecutar(self):
        client = OpenAI(api_key=self.api_key)
        ruta = self.archivo_ruta
        temp_file = None

        try:
            self.safe_ui(self.progress_bar.set, 0.1)
            self.safe_ui(self.output_text.delete, "1.0", "end")

            size_mb = os.path.getsize(ruta) / (1024 * 1024)

            if size_mb > 25:
                self.safe_ui(self.output_text.insert, "end", "Compressing audio...\n")
                audio = AudioSegment.from_file(ruta)
                temp_file = f"temp_{int(time.time())}.mp3"
                audio.export(temp_file, format="mp3", bitrate="96k")
                ruta = temp_file

            self.safe_ui(self.progress_bar.set, 0.3)

            self.safe_ui(self.output_text.insert, "end", "Transcribing...\n")

            with open(ruta, "rb") as f:
                transcription = client.audio.transcriptions.create(
                    model="whisper-1",
                    file=f
                )

            texto = transcription.text

            self.safe_ui(self.progress_bar.set, 0.7)

            modo = self.modo.get()
            prompt = self.obtener_prompt(modo, texto)

            self.safe_ui(self.output_text.insert, "end", "Generating AI output...\n")

            response = client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {"role": "system", "content": "You are an expert study assistant."},
                    {"role": "user", "content": prompt}
                ]
            )

            resultado = response.choices[0].message.content

            self.safe_ui(self.progress_bar.set, 0.9)

            os.makedirs("output", exist_ok=True)
            filename = f"output/Notes_{int(time.time())}.txt"

            with open(filename, "w", encoding="utf-8") as f:
                f.write(resultado)

            self.safe_ui(self.output_text.insert, "end", f"\nSaved: {filename}")
            self.safe_ui(self.progress_bar.set, 1.0)

        except Exception as e:
            self.safe_ui(messagebox.showerror, "Error", str(e))

        finally:
            if temp_file and os.path.exists(temp_file):
                os.remove(temp_file)

            self.safe_ui(self.btn_run.configure, {"state": "normal"})


if __name__ == "__main__":
    app = TranscriptorApp()
    app.mainloop()
