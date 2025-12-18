import os
from pygame import mixer
from config import Config

class SoundManager:
    def __init__(self):
        self.enabled = False
        self.sounds = {}
        self.current_bg = None 
        
        # Inicializamos el mixer de Pygame
        try:
            mixer.init()
            self.enabled = True
            self._load_sounds()
        except ImportError:
            print("⚠️ Pygame no instalado. Audio desactivado.")
        except Exception as e:
            print(f"❌ Error iniciando mixer: {e}")

    def _find_assets_folder(self):
        """Busca la carpeta assets en el directorio actual o en el superior."""
        current_dir = os.path.dirname(os.path.abspath(__file__))
        
        path = os.path.join(current_dir, "..", "assets")
        
        return os.path.abspath(path) if os.path.exists(path) else None  

    def _load_sounds(self):
        '''Carga los archivos de audio según la configuración.'''
        assets_folder = self._find_assets_folder()
        
        if not assets_folder:
            print(f"❌ ERROR CRÍTICO: No se encuentra la carpeta 'assets'.")
            print(f"   (Se buscó cerca de: {os.path.dirname(os.path.abspath(__file__))})")
            return

        # Cargamos los sonidos definidos en settings.json
        sound_map = Config.SETTINGS.get("sounds", {})
        
        # Cargamos cada archivo
        for key, filename in sound_map.items():
            filename_clean = os.path.basename(filename).replace("assets/", "").replace(".mp3", "")
            path = os.path.join(assets_folder, f"{filename_clean}.mp3")
            
            # Verificamos si el archivo existe
            if os.path.exists(path):
                try:
                    sound = mixer.Sound(path)
                    if "bg" in key: sound.set_volume(0.3)
                    if "hurry" in key: sound.set_volume(0.6)
                    self.sounds[key] = sound
                except Exception as e:
                    print(f"❌ Error archivo dañado {filename_clean}: {e}")
            else:
                print(f"⚠️ Audio faltante: {filename_clean}.mp3")

    # Reproduce un efecto de sonido una vez
    def play_effect(self, sound_key: str):
        if self.enabled and sound_key in self.sounds:
            self.sounds[sound_key].play()

    # Reproduce música de fondo en loop
    def play_background(self, sound_key: str):
        if not self.enabled: return
        self.stop_all() 
        if sound_key in self.sounds:
            self.current_bg = self.sounds[sound_key]
            self.current_bg.play(loops=-1)

    # Detiene toda la música y efectos
    def stop_all(self):
        if self.enabled:
            mixer.stop()
            self.current_bg = None