import tkinter as tk
from tkinter import messagebox
import random
import os
import threading
import sys
from typing import Optional, Tuple

# =========================================================
# CONFIGURACIÓN (Centralizada para facilitar cambios)
# =========================================================
class Config:
    TITLE = "Simón Dice - Edición Profesional"
    GEOMETRY = "550x600"
    BG_COLOR = "#f0f0f0"
    
    # Colores
    COLOR_TEXT_PRIMARY = "#333333"
    COLOR_ACCENT_ORANGE = "#FF9800"
    COLOR_SUCCESS = "#4CAF50"
    COLOR_ERROR = "#FF5722"
    COLOR_TIMER = "#E53935"
    
    # Fuentes
    FONT_MAIN = ("Helvetica", 12)
    FONT_BOLD = ("Helvetica", 12, "bold")
    FONT_HEADER = ("Helvetica", 16, "bold")
    
    # Parámetros de Juego
    FILE_RECORD = "simon_record.txt"
    TIME_LIMIT = 15
    SOUND_ENABLED = sys.platform == "win32"

# =========================================================
# GESTOR DE SONIDO (Aislado)
# =========================================================
class SoundManager:
    """Gestiona la reproducción de sonidos de forma segura y sin bloquear la UI."""
    
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
        """Reproduce un sonido en un hilo separado."""
        if not self.enabled or not self.winsound:
            return

        # Usamos threading para no congelar la ventana mientras suena
        thread = threading.Thread(target=self._generate_tone, args=(sound_type,))
        thread.daemon = True
        thread.start()

    def _generate_tone(self, sound_type: str) -> None:
        try:
            if sound_type == "success":
                self.winsound.Beep(1000, 150) # Agudo, corto
            elif sound_type == "error":
                self.winsound.Beep(150, 600)  # Grave, largo
            elif sound_type == "tick":
                self.winsound.Beep(800, 50)   # Tic de reloj
        except Exception as e:
            print(f"Error de audio silenciado: {e}")

# =========================================================
# LÓGICA DEL JUEGO (Modelo)
# =========================================================
class GameLogic:
    """Maneja el estado, las reglas, puntuación y generación de retos."""
    
    def __init__(self):
        self.score = 0
        self.high_score = self._load_record()
        self.current_answer = ""
        self.simon_says = False
        
    def _load_record(self) -> int:
        if not os.path.exists(Config.FILE_RECORD):
            return 0
        try:
            with open(Config.FILE_RECORD, "r") as f:
                content = f.read().strip()
                return int(content) if content.isdigit() else 0
        except IOError:
            return 0

    def save_record(self) -> bool:
        """Guarda el récord. Retorna True si hubo un nuevo récord."""
        if self.score > self.high_score:
            self.high_score = self.score
            try:
                with open(Config.FILE_RECORD, "w") as f:
                    f.write(str(self.high_score))
                return True
            except IOError:
                print("Advertencia: No se pudo guardar el récord en disco.")
        return False

    def generate_turn(self) -> Tuple[str, bool]:
        """Genera un nuevo desafío aleatorio. Retorna (texto_a_mostrar, simon_lo_dijo)."""
        capitals = {
            "Francia": "paris", "España": "madrid", "Italia": "roma", 
            "Alemania": "berlin", "Portugal": "lisboa", "Reino Unido": "londres",
            "Japón": "tokio", "Rusia": "moscu"
        }
        words = ["python", "codigo", "simon", "juego", "ventana", "teclado", "raton"]

        challenge_type = random.choice(['math', 'word', 'capital'])
        text_base = ""

        if challenge_type == 'math':
            a, b = random.randint(1, 20), random.randint(1, 20)
            text_base = f"calcula {a} + {b}"
            self.current_answer = str(a + b)
        
        elif challenge_type == 'word':
            word = random.choice(words)
            text_base = f"escribe '{word}'"
            self.current_answer = word
        
        elif challenge_type == 'capital':
            country, capital = random.choice(list(capitals.items()))
            text_base = f"¿capital de {country}?"
            self.current_answer = capital

        self.simon_says = random.choice([True, False])
        
        # Si Simón lo dice, mostramos "Simón dice: ...". Si no, solo la orden.
        display_text = f"Simón dice: {text_base}" if self.simon_says else text_base.capitalize()
        return display_text, self.simon_says

    def check_answer(self, user_input: str) -> Tuple[bool, str]:
        """Valida la respuesta escrita."""
        user_input = user_input.lower().strip()
        
        if self.simon_says:
            if user_input == self.current_answer:
                self.score += 1
                return True, ""
            else:
                return False, f"¡Incorrecto! La respuesta era '{self.current_answer}'."
        else:
            return False, "¡Simón no dijo nada! No debiste escribir."

    def check_pass(self) -> Tuple[bool, str]:
        """Valida la acción de pasar."""
        if self.simon_says:
            return False, "¡Error! Simón ordenó hacerlo y pasaste."
        else:
            self.score += 1
            return True, ""

# =========================================================
# INTERFAZ GRÁFICA (Vista y Controlador)
# =========================================================
class SimonDiceApp:
    def __init__(self, root: tk.Tk):
        self.root = root
        self.logic = GameLogic()
        self.sound = SoundManager()
        
        # Estado de la UI
        self.timer_left = Config.TIME_LIMIT
        self.timer_id: Optional[str] = None
        self.is_playing = False

        self._setup_window()
        self._build_ui()
        
        # Iniciamos el primer turno
        self.start_new_turn()

    def _setup_window(self):
        self.root.title(Config.TITLE)
        self.root.geometry(Config.GEOMETRY)
        self.root.configure(bg=Config.BG_COLOR)
        # Vinculamos el cierre de ventana a una limpieza correcta
        self.root.protocol("WM_DELETE_WINDOW", self.on_close)

    def _build_ui(self):
        # 1. Panel Superior (Info)
        frame_info = tk.Frame(self.root, bg=Config.BG_COLOR)
        frame_info.pack(pady=20, fill=tk.X)

        self.lbl_record = tk.Label(frame_info, text=f"🏆 Récord: {self.logic.high_score}", 
                                   font=Config.FONT_BOLD, fg=Config.COLOR_ACCENT_ORANGE, bg=Config.BG_COLOR)
        self.lbl_record.pack(side=tk.LEFT, padx=30)

        self.lbl_score = tk.Label(frame_info, text="Puntos: 0", 
                                  font=Config.FONT_MAIN, bg=Config.BG_COLOR)
        self.lbl_score.pack(side=tk.RIGHT, padx=30)

        # 2. Timer
        self.lbl_timer = tk.Label(self.root, text=f"⏱ {Config.TIME_LIMIT}s", 
                                  font=Config.FONT_HEADER, fg=Config.COLOR_TIMER, bg=Config.BG_COLOR)
        self.lbl_timer.pack(pady=10)

        # 3. Instrucción Principal
        self.lbl_instruction = tk.Label(self.root, text="Cargando...", 
                                        font=Config.FONT_HEADER, wraplength=500, bg=Config.BG_COLOR, fg=Config.COLOR_TEXT_PRIMARY)
        self.lbl_instruction.pack(pady=30)

        # 4. Campo de entrada
        self.entry_answer = tk.Entry(self.root, font=("Helvetica", 14), width=25, justify='center')
        self.entry_answer.pack(pady=10)
        # Permitir enviar con la tecla Enter
        self.entry_answer.bind('<Return>', lambda e: self.action_submit())

        # 5. Botones de Acción
        frame_btns = tk.Frame(self.root, bg=Config.BG_COLOR)
        frame_btns.pack(pady=30)

        self.btn_submit = tk.Button(frame_btns, text="¡Hacerlo!", command=self.action_submit,
                                    bg=Config.COLOR_SUCCESS, fg="white", font=Config.FONT_BOLD, width=12, height=2)
        self.btn_submit.pack(side=tk.LEFT, padx=15)

        self.btn_pass = tk.Button(frame_btns, text="Pasar / Ignorar", command=self.action_pass,
                                  bg=Config.COLOR_ERROR, fg="white", font=Config.FONT_BOLD, width=15, height=2)
        self.btn_pass.pack(side=tk.LEFT, padx=15)

        # 6. Botón de Reinicio
        self.btn_restart = tk.Button(self.root, text="Reiniciar Partida", command=self.restart_game,
                                     state=tk.DISABLED, font=Config.FONT_MAIN)
        self.btn_restart.pack(side=tk.BOTTOM, pady=20)

    # --- Lógica del Flujo del Juego ---

    def start_new_turn(self):
        """Inicia un nuevo turno: limpia UI, genera pregunta, reinicia timer."""
        if not self.root.winfo_exists(): return
        
        self.is_playing = True
        self.entry_answer.delete(0, tk.END)
        self.entry_answer.config(state=tk.NORMAL)
        self.entry_answer.focus()
        
        # Pedimos al modelo los datos del nuevo turno
        text, _ = self.logic.generate_turn()
        self.lbl_instruction.config(text=text, fg="black")
        
        self.start_timer()

    def start_timer(self):
        self.stop_timer()
        self.timer_left = Config.TIME_LIMIT
        self._update_timer()

    def stop_timer(self):
        if self.timer_id:
            try:
                self.root.after_cancel(self.timer_id)
            except ValueError: pass
            self.timer_id = None

    def _update_timer(self):
        if not self.is_playing: return
        
        self.lbl_timer.config(text=f"⏱ {self.timer_left}s")
        
        if self.timer_left <= 0:
            self.sound.play("error")
            self.handle_game_over("¡Se acabó el tiempo!")
        else:
            self.timer_left -= 1
            # Llamada recursiva cada 1 segundo (1000 ms)
            self.timer_id = self.root.after(1000, self._update_timer)

    # --- Acciones del Usuario ---

    def action_submit(self):
        """El usuario decide realizar la acción."""
        if not self.is_playing: return
        self.stop_timer()

        answer = self.entry_answer.get()
        success, msg = self.logic.check_answer(answer)
        self._process_result(success, msg)

    def action_pass(self):
        """El usuario decide ignorar la orden."""
        if not self.is_playing: return
        self.stop_timer()

        success, msg = self.logic.check_pass()
        self._process_result(success, msg)

    def _process_result(self, success: bool, fail_msg: str):
        if success:
            self.sound.play("success")
            self.lbl_score.config(text=f"Puntos: {self.logic.score}")
            # Pequeña pausa para UX antes del siguiente turno
            self.root.after(500, self.start_new_turn)
        else:
            self.sound.play("error")
            self.handle_game_over(fail_msg)

    def handle_game_over(self, reason: str):
        self.is_playing = False
        self.stop_timer()
        
        # Guardar récord
        new_record = self.logic.save_record()
        
        # Actualizar UI
        self.lbl_instruction.config(text=f"FIN DEL JUEGO\n{reason}", fg="red")
        self.entry_answer.config(state=tk.DISABLED)
        self.btn_restart.config(state=tk.NORMAL)
        self.btn_submit.config(state=tk.DISABLED)
        self.btn_pass.config(state=tk.DISABLED)

        if new_record:
            self.lbl_record.config(text=f"🏆 Récord: {self.logic.high_score}")
            messagebox.showinfo("¡Nuevo Récord!", f"¡Increíble! Nuevo récord: {self.logic.high_score}")
        else:
            messagebox.showinfo("Juego Terminado", f"{reason}\nPuntuación final: {self.logic.score}")

    def restart_game(self):
        self.logic.score = 0
        self.lbl_score.config(text="Puntos: 0")
        
        self.btn_submit.config(state=tk.NORMAL)
        self.btn_pass.config(state=tk.NORMAL)
        self.btn_restart.config(state=tk.DISABLED)
        
        self.start_new_turn()

    def on_close(self):
        """Detiene procesos en segundo plano antes de destruir la ventana."""
        self.is_playing = False
        self.stop_timer()
        self.root.destroy()

if __name__ == "__main__":
    try:
        root = tk.Tk()
        app = SimonDiceApp(root)
        root.mainloop()
    except Exception as e:
        sys.stderr.write(f"Error crítico: {e}\n")