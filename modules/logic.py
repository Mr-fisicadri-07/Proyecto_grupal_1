import random
import os
import unicodedata
from typing import Tuple
from config import Config

class GameLogic:
    def __init__(self):
        self.score = 0
        self.high_score = self._load_record()
        self.current_answer = ""
        self.simon_says = False
        self.last_country = "" 

    # Carga el récord guardado desde el archivo
    def _load_record(self) -> int:
        # Si no existe el archivo, devolvemos 0
        if not os.path.exists(Config.RECORD_FILE): return 0
        # Intentamos leer el récord guardado
        try:
            with open(Config.RECORD_FILE, "r") as f:
                content = f.read().strip()
                return int(content) if content.isdigit() else 0
        except: return 0

    # Guarda el récord si el puntaje actual lo supera
    def save_record(self) -> bool:
        if self.score > self.high_score:
            self.high_score = self.score
            try:
                with open(Config.RECORD_FILE, "w") as f: 
                    f.write(str(self.high_score))
                return True
            except IOError:
                return False
        return False

    # Genera una nueva instrucción para el turno actual
    def generate_turn(self) -> Tuple[str, bool]:
        self.last_country = ""
        
        # Recuperamos datos del JSON cargado
        words = Config.GAME_CONTENT.get("palabras", [])
        capitals = Config.GAME_CONTENT.get("capitales", [])
        
        # Elegimos el modo del turno
        mode = 'capital' if (capitals and random.random() < 0.4) else random.choice(['math', 'word'])
        text_display = ""
        
        # Generamos la instrucción según el modo
        if mode == 'math':
            a, b = random.randint(1, 20), random.randint(1, 20)
            text_display = f"calcula {a} + {b}"
            self.current_answer = str(a + b)
            
        elif mode == 'word' and words:
            word = random.choice(words)
            text_display = f"escribe '{word}'"
            self.current_answer = word
            
        elif mode == 'capital' and capitals:
            item = random.choice(capitals)
            self.last_country = item["pais"]
            self.current_answer = item["respuesta"]
            text_display = f"¿capital de {self.last_country}?"
        else:
            # Fallback por si los JSON están vacíos
            text_display = "escribe 'error'"
            self.current_answer = "error"
        
        # Decidimos si es "Simón dice" o no
        self.simon_says = random.choice([True, False])
        
        # Devolvemos la instrucción y si es "Simón dice"
        if self.simon_says:
            return f"Simón dice: {text_display}", True
        else:
            return text_display.capitalize(), False

    # Normaliza el texto para comparaciones
    def _normalize(self, text: str) -> str:
        """
        Helper para limpiar el texto: 
        1. Separa los caracteres de sus tildes (NFD).
        2. Filtra las marcas de acento (Mn - Mark, nonspacing).
        3. Convierte a minúsculas y quita espacios extra.
        """
        return ''.join(
            c for c in unicodedata.normalize('NFD', text)
            if unicodedata.category(c) != 'Mn'
        ).lower().strip()

    # Verifica la respuesta del usuario
    def check_answer(self, user_input: str) -> Tuple[bool, str]:
        # Normalizamos ambas respuestas para comparación
        user_clean = self._normalize(user_input)
        answer_clean = self._normalize(self.current_answer)

        # Verificamos según si es "Simón dice" o no
        if self.simon_says:
            if user_clean == answer_clean:
                self.score += 1
                return True, ""
            # Mostramos la respuesta original (con tilde) para que el usuario aprenda
            return False, f"Era '{self.current_answer}'"
        
        return False, "¡Simón no dijo nada!"

    # Verifica si el usuario puede pasar el turno
    def check_pass(self) -> Tuple[bool, str]:
        if self.simon_says:
            return False, "¡Simón ordenó hacerlo!"
        self.score += 1
        return True, ""