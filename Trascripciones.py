import whisper
from openai import OpenAI
import os

# --- CONFIGURACIÓN ---
# 1. Pon aquí tu API Key de OpenAI para el resumen
# (Consíguela en platform.openai.com)
client = OpenAI(api_key="TU_API_KEY_AQUÍ")

def procesar_audio(ruta_audio):
    # FASE 1: Transcripción con Whisper (Gratis, usa tu PC)
    print(" Paso 1: Transcribiendo audio... Ten paciencia.")
    modelo = whisper.load_model("small") # 'small' es rápido y bueno para español
    resultado = modelo.transcribe(ruta_audio, language="es")
    texto_completo = resultado["text"]
    
    # Guardamos la transcripción bruta
    with open("transcripcion.txt", "w", encoding="utf-8") as f:
        f.write(texto_completo)
    print("✅ Transcripción guardada en 'transcripcion.txt'")

    # FASE 2: Resumen con GPT (Necesita unos céntimos de saldo en OpenAI)
    print(" Paso 2: Generando resumen inteligente...")
    response = client.chat.completions.create(
        model="gpt-4o-mini", # Barato y muy rápido
        messages=[
            {"role": "system", "content": "Eres un experto en síntesis. Resume el siguiente texto en puntos clave y extrae las conclusiones principales."},
            {"role": "user", "content": texto_completo}
        ]
    )
    
    resumen = response.choices[0].message.content
    
    # Guardamos el resumen
    with open("resumen.txt", "w", encoding="utf-8") as f:
        f.write(resumen)
    print("✅ Resumen guardado en 'resumen.txt'")

# --- EJECUCIÓN ---
archivo = "clase_historia.mp3" # Asegúrate de que el audio esté en la misma carpeta
if os.path.exists(archivo):
    procesar_audio(archivo)
else:
    print(f"❌ No encuentro el archivo {archivo}")