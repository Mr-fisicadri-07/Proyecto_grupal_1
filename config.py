import json
import os

class Config:
    # Rutas relativas base
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))
    DATA_DIR = os.path.join(BASE_DIR, 'data')
    ASSETS_DIR = os.path.join(BASE_DIR, 'assets')
    RECORD_FILE = os.path.join(BASE_DIR, 'simon_record.txt')

    # Variables que cargaremos
    SETTINGS = {}
    GAME_CONTENT = {}
    
    @classmethod
    def load_configurations(cls):
        """Carga los JSONs de configuración y datos."""
        try:
            with open(os.path.join(cls.DATA_DIR, 'settings.json'), 'r', encoding='utf-8') as f:
                cls.SETTINGS = json.load(f)
            
            with open(os.path.join(cls.DATA_DIR, 'gamedata.json'), 'r', encoding='utf-8') as f:
                cls.GAME_CONTENT = json.load(f)
                
        except FileNotFoundError as e:
            print(f"❌ Error crítico: No se encuentra el archivo de configuración: {e}")
            # Valores por defecto de emergencia para que no crashee inmediatamente
            cls.SETTINGS = {
                "window": {"title": "Error Carga", "geometry": "400x400", "bg_color": "red"},
                "sounds": {}
            }
            cls.GAME_CONTENT = {"palabras": ["error"], "capitales": []}

# Cargamos la configuración al importar el módulo
Config.load_configurations()