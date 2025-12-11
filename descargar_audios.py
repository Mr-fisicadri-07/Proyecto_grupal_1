import yt_dlp
import os

# Diccionario: Nombre del archivo que necesita el juego -> URL de YouTube
audios = {
    "tiempo": "https://www.youtube.com/watch?v=9SLgQEznnSk",       # Música Wii
    "tiempo_eater": "https://www.youtube.com/watch?v=pu1pOFDFAIw", # Snake Eater
    "poco_tiempo": "https://www.youtube.com/watch?v=aLVr0VfeLmk",  # Majora's Mask
    "fallo": "https://www.youtube.com/watch?v=dtx8Yq9OlK0",        # Bob Esponja
    "derrota": "https://www.youtube.com/watch?v=h0NG7DxV5iE",      # Música triste
    "victoria": "https://www.youtube.com/watch?v=J2_fcFsS9t0",     # Siuuu / Victoria
    "peru": "https://www.youtube.com/watch?v=-TAMMDMKbU8",         # Audio Perú
    "espana": "https://www.youtube.com/watch?v=GWCldYPEsl4",       # Himno España
    "record_50": "https://www.youtube.com/watch?v=oKqIFhQreKM",    # Épico
    "onichan": "https://www.youtube.com/watch?v=p4177gNws_s"       # Easter egg
}

def descargar():
    print("⬇️ INICIANDO DESCARGA DE AUDIOS...")
    
    opciones = {
        'format': 'bestaudio/best',
        'outtmpl': '%(title)s.%(ext)s', # Nombre temporal
        'quiet': True,
        'postprocessors': [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'mp3',
            'preferredquality': '192',
        }],
    }

    for nombre_final, url in audios.items():
        print(f"   ⏳ Procesando: {nombre_final}...")
        
        # Ajustamos el nombre de salida para que sea exactamente lo que pide el juego
        mis_opciones = opciones.copy()
        mis_opciones['outtmpl'] = f"{nombre_final}.%(ext)s"
        
        try:
            with yt_dlp.YoutubeDL(mis_opciones) as ydl:
                ydl.download([url])
            print(f"   ✅ {nombre_final}.mp3 descargado.")
        except Exception as e:
            print(f"   ❌ ERROR con {nombre_final}: Probablemente te falta FFmpeg.")
            print(f"      Intenta descargar este link manualmente: {url}")

if __name__ == "__main__":
    descargar()
    print("\n✅ Proceso terminado. Ahora ejecuta el juego.")