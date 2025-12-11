import tkinter as tk
from tkinter import messagebox
import random
import os
import json
from typing import Tuple

# Intentamos importar pygame
try:
    from pygame import mixer
    _PYGAME_AVAILABLE = True
except ImportError:
    _PYGAME_AVAILABLE = False

# CONFIGURACIÓN
class Config:
    TITLE = "Simón Dice"
    GEOMETRY = "600x700"
    BG_COLOR = "#f0f0f0"
    FILE_RECORD = "simon_record.txt"
    FILE_SOUNDS_CONFIG = "sounds.json"
    TIME_LIMIT = 15

# GESTOR DE SONIDO (SIMPLIFICADO)
class SoundManager:
    def __init__(self):
        self.enabled = _PYGAME_AVAILABLE
        self.sounds = {}
        self.current_bg = None 
        
        if self.enabled:
            mixer.init()
            self._load_sounds()

    def _load_sounds(self):
        # Carga directa del JSON sin comprobaciones de seguridad
        with open(Config.FILE_SOUNDS_CONFIG, 'r') as f:
            mapa_archivos = json.load(f)

        for key, nombre_archivo in mapa_archivos.items():
            # Asumimos directamente que es .mp3
            ruta = f"{nombre_archivo}.mp3"
            self.sounds[key] = mixer.Sound(ruta)
            
            # Ajustes rápidos de volumen
            if "bg" in key: self.sounds[key].set_volume(0.3)
            if "hurry" in key: self.sounds[key].set_volume(0.5)
            if "win" in key: self.sounds[key].set_volume(0.4)

    def play_effect(self, sound_key):
        if self.enabled and sound_key in self.sounds:
            self.sounds[sound_key].play()

    def play_background(self, sound_key):
        if not self.enabled: return
        self.stop_background()
        if sound_key in self.sounds:
            self.current_bg = self.sounds[sound_key]
            self.current_bg.play(loops=-1)

    def stop_background(self):
        if self.current_bg:
            self.current_bg.stop()
            self.current_bg = None

    def stop_all(self):
        if self.enabled:
            mixer.stop()

# LÓGICA DEL JUEGO
class GameLogic:
    def __init__(self):
        self.score = 0
        self.high_score = self._load_record()
        self.current_answer = ""
        self.simon_says = False
        self.last_country = ""
        
        self.datos = {
            "palabras": ["python", "código", "java", "meme", "anime", "gato"],
            "capitales": [
                {"pais": "España", "respuesta": "madrid"},
                {"pais": "Perú", "respuesta": "lima"},
                {"pais": "Francia", "respuesta": "paris"},
                {"pais": "Japón", "respuesta": "tokio"},
                {"pais": "Italia", "respuesta": "roma"}
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

# APP PRINCIPAL
class SimonDiceApp:
    def __init__(self, root: tk.Tk):
        self.root = root
        self.sound = SoundManager()
        self.timer_id = None
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
        frame_top = tk.Frame(self.root, bg=Config.BG_COLOR)
        frame_top.pack(fill="x", pady=10)
        
        self.lbl_score = tk.Label(frame_top, text="Pts: 0", font=("Helvetica", 14), bg=Config.BG_COLOR)
        self.lbl_score.pack(side="left", padx=20)
        
        self.lbl_timer = tk.Label(frame_top, text="15s", font=("Helvetica", 16, "bold"), fg="red", bg=Config.BG_COLOR)
        self.lbl_timer.pack(side="right", padx=20)

        self.lbl_instruction = tk.Label(self.root, text="", font=("Helvetica", 20, "bold"), 
                                        wraplength=500, bg=Config.BG_COLOR, height=4)
        self.lbl_instruction.pack(pady=10)

        self.entry = tk.Entry(self.root, font=("Helvetica", 18), justify='center')
        self.entry.pack(pady=10)
        self.entry.bind('<Return>', lambda e: self.action_submit())

        frame_btns = tk.Frame(self.root, bg=Config.BG_COLOR)
        frame_btns.pack(pady=20)
        
        tk.Button(frame_btns, text="¡HACERLO!", bg="#4CAF50", fg="white", font="bold", 
                  command=self.action_submit, width=12, height=2).pack(side="left", padx=10)
        tk.Button(frame_btns, text="PASAR", bg="#FF9800", fg="white", font="bold", 
                  command=self.action_pass, width=12, height=2).pack(side="left", padx=10)

    def start_new_turn(self):
        if not self.root.winfo_exists(): return
        self.is_playing = True
        
        text, _ = self.logic.generate_turn()
        self.lbl_instruction.config(text=text, fg="black")
        
        self.entry.delete(0, tk.END)
        self.entry.config(state='normal')
        self.entry.focus()

        self.sound.stop_background()
        
        if self.logic.last_country == "España":
            self.sound.play_background("special_espana")
        elif self.logic.last_country == "Perú":
            self.sound.play_background("special_peru")
        else:
            if random.random() < 0.05:
                self.sound.play_effect("easter_egg")
                self.root.after(1500, lambda: self.sound.play_background("bg_normal"))
            else:
                bg = "bg_normal" if random.random() > 0.5 else "bg_eater"
                self.sound.play_background(bg)

        self.timer_left = Config.TIME_LIMIT
        self.stop_timer()
        self._update_timer()

    def _update_timer(self):
        if not self.is_playing: return
        self.lbl_timer.config(text=f"⏱ {self.timer_left}s")
        
        if self.timer_left == 5:
            self.sound.stop_background()
            self.sound.play_effect("hurry")

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
        self.stop_timer()
        success, msg = self.logic.check_answer(self.entry.get())
        self._process_result(success, msg)

    def action_pass(self):
        if not self.is_playing: return
        self.stop_timer()
        success, msg = self.logic.check_pass()
        self._process_result(success, msg)

    def _process_result(self, success, fail_msg):
        self.sound.stop_background()
        if success:
            if self.logic.score == 50:
                self.sound.play_effect("epic_50")
                messagebox.showinfo("¡WOW!", "¡50 PUNTOS!")
            else:
                self.sound.play_effect("win")
            
            self.lbl_score.config(text=f"Pts: {self.logic.score}")
            self.root.after(1500, self.start_new_turn)
        else:
            self.sound.play_effect("fail")
            self.handle_game_over(fail_msg)

    def handle_game_over(self, reason):
        self.is_playing = False
        new_record = self.logic.save_record()
        self.root.after(1000, lambda: self.sound.play_background("gameover"))

        self.lbl_instruction.config(text=f"💀 FIN 💀\n{reason}", fg="red")
        self.entry.config(state='disabled')
        
        msg = f"Récord Nuevo: {self.logic.high_score}" if new_record else f"Puntos: {self.logic.score}"
        
        frame_over = tk.Frame(self.root, bg="#333", relief="raised", bd=5)
        frame_over.place(relx=0.5, rely=0.5, anchor="center", width=400, height=200)
        
        tk.Label(frame_over, text="¡PERDISTE!", fg="red", bg="#333", font=("Arial", 20, "bold")).pack(pady=10)
        tk.Label(frame_over, text=msg, fg="white", bg="#333", font=("Arial", 14)).pack(pady=10)
        tk.Button(frame_over, text="Reintentar", command=self.start_game_session, bg="white").pack(pady=5)
        tk.Button(frame_over, text="Salir", command=self.root.destroy, bg="red", fg="white").pack(pady=5)

if __name__ == "__main__":
    if not _PYGAME_AVAILABLE:
        print("Instala pygame: pip install pygame")
    root = tk.Tk()
    app = SimonDiceApp(root)
    root.mainloop()