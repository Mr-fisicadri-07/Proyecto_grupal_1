import os
from pygame import mixer
from config import Config

class SoundManager:
    def __init__(self):
        self.enabled = False
        self.sounds = {}
        self.current_bg = None 
        
        try:
            mixer.init()
            self.enabled = True
            self._load_sounds()
        except ImportError:
            print("⚠️ Pygame no instalado. Audio desactivado.")
        except Exception as e:
            print(f"❌ Error iniciando mixer: {e}")

    def _load_sounds(self):
        """Carga los audios definidos en settings.json"""
        sound_map = Config.SETTINGS.get("sounds", {})
        
        for key, filename in sound_map.items():
            # Construye la ruta: carpeta assets / nombre archivo .mp3
            path = os.path.join(Config.ASSETS_DIR, f"{filename}.mp3")
            
            if os.path.exists(path):
                try:
                    sound = mixer.Sound(path)
                    if "bg" in key: sound.set_volume(0.3)
                    if "hurry" in key: sound.set_volume(0.6)
                    self.sounds[key] = sound
                except Exception as e:
                    print(f"Error cargando {path}: {e}")
            else:
                print(f"⚠️ Audio no encontrado: {path}")

    def play_effect(self, sound_key: str):
        if self.enabled and sound_key in self.sounds:
            self.sounds[sound_key].play()

    def play_background(self, sound_key: str):
        if not self.enabled: return
        self.stop_all() 
        if sound_key in self.sounds:
            self.current_bg = self.sounds[sound_key]
            self.current_bg.play(loops=-1)

    def stop_all(self):
        if self.enabled:
            mixer.stop()
            self.current_bg = None