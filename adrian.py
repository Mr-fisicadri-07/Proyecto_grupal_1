import tkinter as tk
from tkinter import messagebox
import random
import os
import threading
import sys
from typing import Optional, Tuple
import json

# =========================================================
# CONFIGURACIÓN
# =========================================================
class Config:
    TITLE = "Simón Dice - Edición Profesional"
    GEOMETRY = "600x650"  # Un poco más alto para las reglas
    BG_COLOR = "#f0f0f0"
    
    # Colores
    COLOR_TEXT = "#333333"
    COLOR_ACCENT = "#FF9800"
    COLOR_SUCCESS = "#4CAF50"
    COLOR_ERROR = "#FF5722"
    COLOR_TIMER = "#E53935"
    COLOR_BTN_MENU = "#2196F3"
    
    # Fuentes
    FONT_TEXT = ("Helvetica", 12)
    FONT_BOLD = ("Helvetica", 12, "bold")
    FONT_TITLE = ("Helvetica", 24, "bold")
    FONT_HEADER = ("Helvetica", 16, "bold")
    
    FILE_RECORD = "simon_record.txt"
    TIME_LIMIT = 15
    SOUND_ENABLED = sys.platform == "win32"

# =========================================================
# GESTOR DE SONIDO
# =========================================================
class SoundManager:
    def __init__(self):
        self.enabled = Config.SOUND_ENABLED
        self.winsound = None
        if self.enabled:
            try:
                import winsound
                self.winsound = winsound
            except ImportError:
                self.enabled = False

    def play(self, sound_type: str) -> None:
        if not self.enabled or not self.winsound: return
        threading.Thread(target=self._generate_tone, args=(sound_type,), daemon=True).start()

    def _generate_tone(self, sound_type: str) -> None:
        try:
            if sound_type == "success": self.winsound.Beep(1000, 150)
            elif sound_type == "error": self.winsound.Beep(150, 600)
            elif sound_type == "start": self.winsound.Beep(600, 300)
        except: pass

# =========================================================
# LÓGICA DEL JUEGO
# =========================================================
class GameLogic:
    def __init__(self):
        self.score = 0
        self.high_score = self._load_record()
        self.current_answer = ""
        self.simon_says = False
        
        # Cargar datos del JSON
        self.datos = self._cargar_datos_json()

    def _load_record(self) -> int:
        if not os.path.exists(Config.FILE_RECORD): return 0
        try:
            with open(Config.FILE_RECORD, "r") as f:
                c = f.read().strip()
                return int(c) if c.isdigit() else 0
        except: return 0

    def _cargar_datos_json(self):
        """Carga las preguntas y respuestas desde el archivo JSON."""
        archivo = "datos_juego.json"
        datos_default = {
            "palabras": ["python", "demo"],
            "capitales": [{"pais": "España", "respuesta": "madrid"}]
        }
        
        if not os.path.exists(archivo):
            print(f"Alerta: No se encontró {archivo}, usando datos por defecto.")
            return datos_default
            
        try:
            with open(archivo, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception as e:
            print(f"Error leyendo JSON: {e}")
            return datos_default

    #def save_record(self) -> bool:
    #    if self.score > self.high_score:
    #        self.high_score = self.score
    #        try:
    #            with open(Config.FILE_RECORD, "w") as f: f.write(str(self.high_score))
    #            return True
    #        except: pass
    #    return False

    def generate_turn(self) -> Tuple[str, bool]:
        # Usamos los datos cargados del JSON
        palabras = self.datos.get("palabras", ["error"])
        capitales_lista = self.datos.get("capitales", [])
        
        tipo = random.choice(['math', 'word', 'capital'])
        text_base = ""

        if tipo == 'math':
            # Las matemáticas siguen siendo generadas por código porque son infinitas
            a, b = random.randint(1, 20), random.randint(1, 20)
            text_base = f"calcula {a} + {b}"
            self.current_answer = str(a + b)
            
        elif tipo == 'word':
            word = random.choice(palabras)
            text_base = f"escribe '{word}'"
            self.current_answer = word
            
        elif tipo == 'capital':
            if capitales_lista:
                item = random.choice(capitales_lista)
                pais = item["pais"]
                self.current_answer = item["respuesta"]
                text_base = f"¿capital de {pais}?"
            else:
                # Fallback por si el JSON de capitales está vacío
                text_base = "escribe 'error'"
                self.current_answer = "error"

        self.simon_says = random.choice([True, False])
        display = f"Simón dice: {text_base}" if self.simon_says else text_base.capitalize()
        return display, self.simon_says

    # ... (Los métodos check_answer y check_pass siguen igual) ...
    def check_answer(self, user_input: str) -> Tuple[bool, str]:
        user_input = user_input.lower().strip()
        if self.simon_says:
            return (True, "") if user_input == self.current_answer else (False, f"Era '{self.current_answer}'")
        else:
            return (False, "¡Simón no dijo nada!")

    def check_pass(self) -> Tuple[bool, str]:
        return (False, "¡Simón ordenó hacerlo!") if self.simon_says else (True, "")

# =========================================================
# APP PRINCIPAL (VISTA + CONTROLADOR)
# =========================================================
class SimonDiceApp:
    def __init__(self, root: tk.Tk):
        self.root = root
        self.sound = SoundManager()
        self.timer_id = None
        
        self._setup_window()
        # En lugar de iniciar el juego, mostramos el menú
        self.show_menu()

    def _setup_window(self):
        self.root.title(Config.TITLE)
        self.root.geometry(Config.GEOMETRY)
        self.root.configure(bg=Config.BG_COLOR)
        self.root.protocol("WM_DELETE_WINDOW", self.on_close)

    def clear_window(self):
        """Elimina todos los widgets de la ventana actual."""
        self.stop_timer()
        for widget in self.root.winfo_children():
            widget.destroy()

    # ---------------------------------------------------------
    # PANTALLA 1: MENÚ Y REGLAS
    # ---------------------------------------------------------
    def show_menu(self):
        self.clear_window()
        
        frame = tk.Frame(self.root, bg=Config.BG_COLOR, padx=20, pady=20)
        frame.pack(expand=True, fill="both")

        # Título
        tk.Label(frame, text="🧠 SIMÓN DICE", font=Config.FONT_TITLE, 
                 bg=Config.BG_COLOR, fg=Config.COLOR_ACCENT).pack(pady=(20, 10))
        
        tk.Label(frame, text="Edición Profesional", font=Config.FONT_BOLD, 
                 bg=Config.BG_COLOR, fg="#666").pack(pady=(0, 30))

        # Reglas
        reglas = (
            "📜 REGLAS DEL JUEGO:\n\n"
            "1. Si la orden empieza por 'Simón dice':\n"
            "   Debes obedecer (calcular, escribir, etc.) y pulsar '¡Hacerlo!'.\n\n"
            "2. Si la orden NO empieza por 'Simón dice':\n"
            "   ¡NO HAGAS NADA! Debes pulsar el botón 'Pasar / Ignorar'.\n\n"
            "3. Tienes 15 segundos por turno.\n\n"
            "4. Si fallas o se acaba el tiempo, pierdes."
        )

        lbl_reglas = tk.Label(frame, text=reglas, font=Config.FONT_TEXT, 
                              justify="left", bg="white", relief="groove", borderwidth=2, padx=15, pady=15)
        lbl_reglas.pack(pady=20, fill="x")

        # Botón Inicio
        btn_start = tk.Button(frame, text="¡ENTENDIDO, JUGAR!", command=self.start_game_session,
                              bg=Config.COLOR_SUCCESS, fg="white", font=Config.FONT_HEADER, height=2)
        btn_start.pack(pady=30, fill="x")

    # ---------------------------------------------------------
    # PANTALLA 2: JUEGO
    # ---------------------------------------------------------
    def start_game_session(self):
        """Configura la sesión de juego."""
        self.clear_window()
        self.sound.play("start")
        self.logic = GameLogic() # Reiniciar lógica
        self.is_playing = True
        self.timer_left = Config.TIME_LIMIT
        
        self._build_game_ui()
        self.start_new_turn()

    def _build_game_ui(self):
        # Header Info
        frame_info = tk.Frame(self.root, bg=Config.BG_COLOR)
        frame_info.pack(pady=15, fill=tk.X)

        self.lbl_record = tk.Label(frame_info, text=f"🏆 Récord: {self.logic.high_score}", 
                                   font=Config.FONT_BOLD, fg=Config.COLOR_ACCENT, bg=Config.BG_COLOR)
        self.lbl_record.pack(side=tk.LEFT, padx=20)
        
        # Botón Menú pequeño
        tk.Button(frame_info, text="Menú Principal", command=self.show_menu,
                  font=("Helvetica", 9), bg="#999", fg="white").pack(side=tk.RIGHT, padx=20)

        self.lbl_score = tk.Label(self.root, text="Puntos: 0", font=Config.FONT_HEADER, bg=Config.BG_COLOR)
        self.lbl_score.pack(pady=5)

        # Timer
        self.lbl_timer = tk.Label(self.root, text=f"⏱ {Config.TIME_LIMIT}s", 
                                  font=Config.FONT_HEADER, fg=Config.COLOR_TIMER, bg=Config.BG_COLOR)
        self.lbl_timer.pack(pady=5)

        # Instrucción
        self.lbl_instruction = tk.Label(self.root, text="...", font=("Helvetica", 18, "bold"), 
                                        wraplength=550, bg=Config.BG_COLOR, fg=Config.COLOR_TEXT)
        self.lbl_instruction.pack(pady=20)

        # Input
        self.entry_answer = tk.Entry(self.root, font=("Helvetica", 16), width=20, justify='center')
        self.entry_answer.pack(pady=10)
        self.entry_answer.bind('<Return>', lambda e: self.action_submit())

        # Botones Acción
        frame_btns = tk.Frame(self.root, bg=Config.BG_COLOR)
        frame_btns.pack(pady=20)

        self.btn_submit = tk.Button(frame_btns, text="¡Hacerlo!", command=self.action_submit,
                                    bg=Config.COLOR_SUCCESS, fg="white", font=Config.FONT_BOLD, width=12, height=2)
        self.btn_submit.pack(side=tk.LEFT, padx=10)

        self.btn_pass = tk.Button(frame_btns, text="Pasar", command=self.action_pass,
                                  bg=Config.COLOR_ERROR, fg="white", font=Config.FONT_BOLD, width=12, height=2)
        self.btn_pass.pack(side=tk.LEFT, padx=10)
        
        # Botones Fin de Juego (ocultos al inicio)
        self.frame_gameover = tk.Frame(self.root, bg=Config.BG_COLOR)
        # Se empaquetará solo al perder

        self.btn_retry = tk.Button(self.frame_gameover, text="Intentar de nuevo", command=self.start_game_session,
                                   bg=Config.COLOR_ACCENT, fg="white", font=Config.FONT_BOLD)
        self.btn_retry.pack(side=tk.LEFT, padx=10)
        
        self.btn_back_menu = tk.Button(self.frame_gameover, text="Volver al Menú", command=self.show_menu,
                                       bg="#607D8B", fg="white", font=Config.FONT_BOLD)
        self.btn_back_menu.pack(side=tk.LEFT, padx=10)

    # --- Lógica de Turnos ---
    def start_new_turn(self):
        if not self.root.winfo_exists(): return
        self.is_playing = True
        
        self.entry_answer.delete(0, tk.END)
        self.entry_answer.config(state=tk.NORMAL)
        self.entry_answer.focus()
        
        text, _ = self.logic.generate_turn()
        self.lbl_instruction.config(text=text, fg="black")
        
        self.start_timer()

    def start_timer(self):
        self.stop_timer()
        self.timer_left = Config.TIME_LIMIT
        self._update_timer()

    def stop_timer(self):
        if self.timer_id:
            try: self.root.after_cancel(self.timer_id)
            except: pass
            self.timer_id = None

    def _update_timer(self):
        if not self.is_playing: return
        self.lbl_timer.config(text=f"⏱ {self.timer_left}s")
        if self.timer_left <= 0:
            self.sound.play("error")
            self.handle_game_over("¡TIEMPO AGOTADO!")
        else:
            self.timer_left -= 1
            self.timer_id = self.root.after(1000, self._update_timer)

    # --- Acciones ---
    def action_submit(self):
        if not self.is_playing: return
        self.stop_timer()
        success, msg = self.logic.check_answer(self.entry_answer.get())
        self._process_result(success, msg)

    def action_pass(self):
        if not self.is_playing: return
        self.stop_timer()
        success, msg = self.logic.check_pass()
        self._process_result(success, msg)

    def _process_result(self, success, fail_msg):
        if success:
            self.sound.play("success")
            self.lbl_score.config(text=f"Puntos: {self.logic.score}")
            self.root.after(500, self.start_new_turn)
        else:
            self.sound.play("error")
            self.handle_game_over(fail_msg)

    def handle_game_over(self, reason):
        self.is_playing = False
        new_record = self.logic.save_record()
        
        self.lbl_instruction.config(text=f"💀 GAME OVER 💀\n{reason}", fg="red")
        self.entry_answer.config(state=tk.DISABLED)
        self.btn_submit.config(state=tk.DISABLED)
        self.btn_pass.config(state=tk.DISABLED)
        
        # Mostrar botones de reinicio/menú
        self.frame_gameover.pack(pady=20)

        msg = f"¡Nuevo récord: {self.logic.high_score}!" if new_record else f"Puntos: {self.logic.score}"
        messagebox.showinfo("Fin de partida", f"{reason}\n{msg}")

    def on_close(self):
        self.is_playing = False
        self.stop_timer()
        self.root.destroy()

if __name__ == "__main__":
    try:
        root = tk.Tk()
        app = SimonDiceApp(root)
        root.mainloop()
    except Exception as e:
        sys.stderr.write(f"Error: {e}\n")