import tkinter as tk
from tkinter import messagebox
import random
import os
import sys
from typing import Tuple

# Intentamos importar pygame para el audio
try:
    from pygame import mixer
    _PYGAME_AVAILABLE = True
except ImportError:
    _PYGAME_AVAILABLE = False

# =========================================================
# 1. CONFIGURACIÓN
# =========================================================
class Config:
    TITLE = "Simón Dice: Final Edition (No Keys)"
    GEOMETRY = "600x700"
    BG_COLOR = "#f0f0f0"
    
    FILE_RECORD = "simon_record.txt"
    PASS_LOCK_TIME = 500    # 3 segundos bloqueo botón pasar
    
    # MAPA DE SONIDOS
    SOUND_MAP = {
        "bg_normal": "tiempo_wii",    # 90% probabilidad
        "bg_rare": "snake_eater",     # 10% probabilidad
        "hurry": "hurry",             # Últimos 5 segundos
        
        # Sonidos de Derrota (50/50)
        "fail_1": "fallo",            # Bob Esponja
        "fail_2": "derrota",          # Canción triste
        
        # Especiales por País
        "special_peru": "peru",       
        "special_espana": "espana",   
        "special_japon": "onichan",   
        
        "epic_50": "epic_50",         # Al llegar a 50
    }

# =========================================================
# 2. GESTOR DE SONIDO
# =========================================================
class SoundManager:
    def __init__(self):
        self.enabled = _PYGAME_AVAILABLE
        self.sounds = {}
        self.current_bg = None 
        
        if self.enabled:
            try:
                mixer.init()
                self._load_sounds()
            except Exception as e:
                print(f"Error iniciando mixer: {e}")
                self.enabled = False

    def _load_sounds(self):
        extensiones = [".mp3", ".wav", ".m4a", ".ogg"]

        for key, nombre_base in Config.SOUND_MAP.items():
            cargado = False
            for ext in extensiones:
                ruta = f"{nombre_base}{ext}"
                if os.path.exists(ruta):
                    try:
                        self.sounds[key] = mixer.Sound(ruta)
                        cargado = True
                        # Ajustes de volumen
                        if "bg" in key: self.sounds[key].set_volume(0.3)
                        if "hurry" in key: self.sounds[key].set_volume(0.6)
                        break 
                    except Exception as e:
                        print(f"Error cargando {ruta}: {e}")
            
            if not cargado:
                print(f"⚠️ No se encontró audio para: {nombre_base} (Clave: {key})")

    def play_effect(self, sound_key):
        if self.enabled and sound_key in self.sounds:
            self.sounds[sound_key].play()

    def play_background(self, sound_key):
        if not self.enabled: return
        self.stop_all() 
        if sound_key in self.sounds:
            self.current_bg = self.sounds[sound_key]
            self.current_bg.play(loops=-1)

    def stop_all(self):
        """Para todos los sonidos inmediatamente."""
        if self.enabled:
            mixer.stop()
            self.current_bg = None

# =========================================================
# 3. LÓGICA DEL JUEGO
# =========================================================
class GameLogic:
    def __init__(self):
        self.score = 0
        self.high_score = self._load_record()
        self.current_answer = ""
        self.simon_says = False
        self.last_country = "" 
        
        self.datos = {
            "palabras": ["python", "código", "java", "meme", "anime", "gato", "perro", "hola"],
            "capitales": [
                {"pais": "España", "respuesta": "madrid"},
                {"pais": "Perú", "respuesta": "lima"},
                {"pais": "Japón", "respuesta": "tokio"},
                {"pais": "Francia", "respuesta": "paris"},
                {"pais": "Italia", "respuesta": "roma"},
                {"pais": "Argentina", "respuesta": "buenos aires"}
            ]
        }

    def _load_record(self) -> int:
        if not os.path.exists(Config.FILE_RECORD): return 0
        try:
            with open(Config.FILE_RECORD, "r") as f:
                return int(f.read().strip())
        except: return 0

    def save_record(self) -> bool:
        if self.score > self.high_score:
            self.high_score = self.score
            with open(Config.FILE_RECORD, "w") as f: f.write(str(self.high_score))
            return True
        return False

    def generate_turn(self) -> Tuple[str, bool]:
        self.last_country = ""
        tipo = random.choice(['math', 'word', 'capital'])
        
        if random.random() < 0.4: tipo = 'capital' 

        if tipo == 'math':
            a, b = random.randint(1, 20), random.randint(1, 20)
            text_base = f"calcula {a} + {b}"
            self.current_answer = str(a + b)
        elif tipo == 'word':
            word = random.choice(self.datos["palabras"])
            text_base = f"escribe '{word}'"
            self.current_answer = word
        elif tipo == 'capital':
            item = random.choice(self.datos["capitales"])
            pais = item["pais"]
            self.current_answer = item["respuesta"]
            text_base = f"¿capital de {pais}?"
            self.last_country = pais

        self.simon_says = random.choice([True, False])
        display = f"Simón dice: {text_base}" if self.simon_says else text_base.capitalize()
        return display, self.simon_says

    def check_answer(self, user_input: str) -> Tuple[bool, str]:
        if self.simon_says:
            if user_input.lower().strip() == self.current_answer:
                self.score += 1
                return (True, "")
            return (False, f"Era '{self.current_answer}'")
        return (False, "¡Simón no dijo nada!")

    def check_pass(self) -> Tuple[bool, str]:
        if self.simon_says:
            return (False, "¡Simón ordenó hacerlo!")
        self.score += 1
        return (True, "")

# =========================================================
# 4. APP PRINCIPAL
# =========================================================
class SimonDiceApp:
    def __init__(self, root: tk.Tk):
        self.root = root
        self.sound = SoundManager()
        self.timer_id = None
        self.hurry_triggered = False # Flag para música tensión

        self._setup_window()
        self.show_menu()

    def _setup_window(self):
        self.root.title(Config.TITLE)
        self.root.geometry(Config.GEOMETRY)
        self.root.configure(bg=Config.BG_COLOR)

    def clear_window(self):
        self.stop_timer()
        self.sound.stop_all() 
        for widget in self.root.winfo_children():
            widget.destroy()

    def show_menu(self):
        self.clear_window()
        frame = tk.Frame(self.root, bg=Config.BG_COLOR)
        frame.pack(expand=True, fill="both", padx=20, pady=20)

        tk.Label(frame, text="🤡 SIMÓN DICE 🤡", font=("Helvetica", 28, "bold"), 
                 bg=Config.BG_COLOR, fg="#FF5722").pack(pady=20)
        
        tk.Button(frame, text="JUGAR AHORA", command=self.start_game_session,
                        bg="#4CAF50", fg="white", font=("Helvetica", 16, "bold"), height=2).pack(pady=50, fill="x")

    def start_game_session(self):
        self.clear_window()
        self.logic = GameLogic()
        self.is_playing = True
        self._build_game_ui()
        self.start_new_turn()

    def _build_game_ui(self):
        self.frame_top = tk.Frame(self.root, bg=Config.BG_COLOR)
        self.frame_top.pack(fill="x", pady=10)
        
        self.lbl_score = tk.Label(self.frame_top, text="Pts: 0", font=("Helvetica", 14), bg=Config.BG_COLOR)
        self.lbl_score.pack(side="left", padx=20)
        
        self.lbl_timer = tk.Label(self.frame_top, text="15s", font=("Helvetica", 16, "bold"), fg="red", bg=Config.BG_COLOR)
        self.lbl_timer.pack(side="right", padx=20)

        self.game_container = tk.Frame(self.root, bg=Config.BG_COLOR)
        self.game_container.pack(fill="both", expand=True)

        self._build_normal_turn_ui()

    def _build_normal_turn_ui(self):
        for widget in self.game_container.winfo_children(): widget.destroy()

        self.lbl_instruction = tk.Label(self.game_container, text="", font=("Helvetica", 20, "bold"), 
                                        wraplength=500, bg=Config.BG_COLOR, height=4)
        self.lbl_instruction.pack(pady=10)

        self.entry = tk.Entry(self.game_container, font=("Helvetica", 18), justify='center')
        self.entry.pack(pady=10)
        self.entry.bind('<Return>', lambda e: self.action_submit())

        frame_btns = tk.Frame(self.game_container, bg=Config.BG_COLOR)
        frame_btns.pack(pady=20)
        
        tk.Button(frame_btns, text="¡HACERLO!", bg="#4CAF50", fg="white", font="bold", 
                  command=self.action_submit, width=12, height=2).pack(side="left", padx=10)
        
        self.btn_pass = tk.Button(frame_btns, text="PASAR", bg="#FF9800", fg="white", font="bold", 
                  command=self.action_pass, width=12, height=2)
        self.btn_pass.pack(side="left", padx=10)

    # --- CÁLCULO DE DIFICULTAD ---
    def get_difficulty_time(self):
        score = self.logic.score
        if score >= 100: return 3
        if score >= 50: return 5
        if score >= 25: return 7.5
        if score >= 10: return 10
        return 15 # Base

    # --- GESTIÓN DE TURNO ---
    def start_new_turn(self):
        if not self.root.winfo_exists(): return
        self.is_playing = True
        self.hurry_triggered = False 

        text, _ = self.logic.generate_turn()
        self.lbl_instruction.config(text=text, fg="black")
        
        self.entry.delete(0, tk.END)
        self.entry.config(state='normal')
        self.entry.focus()
        
        if hasattr(self, 'btn_pass'):
            self.btn_pass.config(state='disabled', bg="#cccccc") 
            self.root.after(Config.PASS_LOCK_TIME, self.enable_pass_button)

        # Selección de audio
        self.sound.stop_all()
        if self.logic.last_country == "España":
            self.sound.play_background("special_espana")
        elif self.logic.last_country == "Perú":
            self.sound.play_background("special_peru")
        elif self.logic.last_country == "Japón":
            self.sound.play_effect("special_japon") 
            self.root.after(1500, lambda: self.sound.play_background("bg_normal"))
        else:
            if random.random() < 0.10:
                self.sound.play_background("bg_rare")
            else:
                self.sound.play_background("bg_normal")

        # ESTABLECER TIEMPO SEGÚN DIFICULTAD
        self.timer_left = self.get_difficulty_time()
        self.stop_timer()
        self._update_timer()

    def enable_pass_button(self):
        if self.is_playing and hasattr(self, 'btn_pass') and self.btn_pass.winfo_exists():
            self.btn_pass.config(state='normal', bg="#FF9800")

    def _update_timer(self):
        if not self.is_playing: return
        
        # Mostrar tiempo
        if isinstance(self.timer_left, float):
            self.lbl_timer.config(text=f"⏱ {self.timer_left:.1f}s")
        else:
            self.lbl_timer.config(text=f"⏱ {self.timer_left}s")
        
        # LÓGICA DE TENSIÓN
        if self.timer_left <= 5 and not self.hurry_triggered:
            self.hurry_triggered = True 
            self.sound.stop_all() 
            self.sound.play_background("hurry")

        if self.timer_left <= 0:
            self.handle_game_over("¡SE ACABÓ EL TIEMPO!")
        else:
            self.timer_left -= 1
            self.timer_id = self.root.after(1000, self._update_timer)

    def stop_timer(self):
        if self.timer_id:
            self.root.after_cancel(self.timer_id)
            self.timer_id = None

    def action_submit(self):
        if not self.is_playing: return
        self.sound.stop_all() 
        self.stop_timer()
        success, msg = self.logic.check_answer(self.entry.get())
        self._process_result(success, msg)

    def action_pass(self):
        if not self.is_playing: return
        if hasattr(self, 'btn_pass') and self.btn_pass['state'] == 'disabled': return 
        self.sound.stop_all() 
        self.stop_timer()
        success, msg = self.logic.check_pass()
        self._process_result(success, msg)

    def _process_result(self, success, fail_msg):
        self.sound.stop_all()
        if success:
            self.lbl_instruction.config(text="✨ ¡CORRECTO! ✨", fg="#4CAF50")
            self.entry.delete(0, tk.END)
            self.entry.config(state='disabled')
            if hasattr(self, 'btn_pass'): self.btn_pass.config(state='disabled') 
            
            if self.logic.score == 50:
                self.sound.play_effect("epic_50")
                messagebox.showinfo("¡INCREÍBLE!", "¡50 PUNTOS!")
            
            self.lbl_score.config(text=f"Pts: {self.logic.score}")
            self.root.after(2000, self.start_new_turn)
        else:
            sonido_fail = "fail_1" if random.random() < 0.5 else "fail_2"
            self.sound.play_effect(sonido_fail)
            self.handle_game_over(fail_msg)

    def handle_game_over(self, reason):
        self.is_playing = False
        new_record = self.logic.save_record()
        
        for widget in self.game_container.winfo_children(): widget.destroy()

        tk.Label(self.game_container, text=f"💀 FIN 💀\n{reason}", 
                 font=("Helvetica", 20, "bold"), fg="red", bg=Config.BG_COLOR).pack(pady=20)
        
        msg = f"Récord Nuevo: {self.logic.high_score}" if new_record else f"Puntos: {self.logic.score}"
        
        frame_over = tk.Frame(self.root, bg="#333", relief="raised", bd=5)
        frame_over.place(relx=0.5, rely=0.5, anchor="center", width=400, height=200)
        tk.Label(frame_over, text="¡PERDISTE!", fg="red", bg="#333", font=("Arial", 20, "bold")).pack(pady=10)
        tk.Label(frame_over, text=msg, fg="white", bg="#333", font=("Arial", 14)).pack(pady=10)
        tk.Button(frame_over, text="Reintentar", command=self.start_game_session, bg="white").pack(pady=5)
        tk.Button(frame_over, text="Salir", command=self.root.destroy, bg="red", fg="white").pack(pady=5)

if __name__ == "__main__":
    if not _PYGAME_AVAILABLE:
        print("NOTA: Instala pygame (pip install pygame) para los audios.")
        
    root = tk.Tk()
    app = SimonDiceApp(root)
    root.mainloop()