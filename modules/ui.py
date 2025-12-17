import tkinter as tk
from tkinter import messagebox
import random
from config import Config
from modules.logic import GameLogic
from modules.sound import SoundManager

class SimonDiceApp:
    def __init__(self, root: tk.Tk):
        self.root = root
        
        # Cargar configuración visual desde JSON
        win_conf = Config.SETTINGS.get("window", {})
        self.bg_color = win_conf.get("bg_color", "#f0f0f0")
        
        self.root.title(win_conf.get("title", "Simón Dice"))
        self.root.geometry(win_conf.get("geometry", "600x700"))
        self.root.configure(bg=self.bg_color)

        self.sound_manager = SoundManager()
        self.logic = None
        self.timer_id = None
        self.timer_val = 0
        self.hurry_mode = False
        self.is_playing = False

        self.show_menu()

    def clear_window(self):
        self._stop_timer()
        self.sound_manager.stop_all() 
        for widget in self.root.winfo_children():
            widget.destroy()

    def show_menu(self):
        self.clear_window()
        frame = tk.Frame(self.root, bg=self.bg_color)
        frame.pack(expand=True, fill="both", padx=20, pady=20)

        tk.Label(frame, text="🤡 SIMÓN DICE 🤡", font=("Helvetica", 28, "bold"), 
                 bg=self.bg_color, fg="#FF5722").pack(pady=20)
        
        tk.Button(frame, text="JUGAR AHORA", command=self.start_game_session,
                  bg="#4CAF50", fg="white", font=("Helvetica", 16, "bold"), height=2).pack(pady=50, fill="x")

    def start_game_session(self):
        self.clear_window()
        self.logic = GameLogic()
        self.is_playing = True
        self._build_game_ui()
        self.start_new_turn()

    def _build_game_ui(self):
        self.frame_top = tk.Frame(self.root, bg=self.bg_color)
        self.frame_top.pack(fill="x", pady=10)
        
        self.lbl_score = tk.Label(self.frame_top, text="Pts: 0", font=("Helvetica", 14), bg=self.bg_color)
        self.lbl_score.pack(side="left", padx=20)
        
        self.lbl_timer = tk.Label(self.frame_top, text="15s", font=("Helvetica", 16, "bold"), 
                                  fg="red", bg=self.bg_color)
        self.lbl_timer.pack(side="right", padx=20)

        self.game_container = tk.Frame(self.root, bg=self.bg_color)
        self.game_container.pack(fill="both", expand=True)

        self.lbl_instruction = tk.Label(self.game_container, text="", font=("Helvetica", 20, "bold"), 
                                        wraplength=500, bg=self.bg_color, height=4)
        self.lbl_instruction.pack(pady=10)

        self.entry = tk.Entry(self.game_container, font=("Helvetica", 18), justify='center')
        self.entry.pack(pady=10)
        self.entry.bind('<Return>', lambda e: self.action_submit())

        frame_btns = tk.Frame(self.game_container, bg=self.bg_color)
        frame_btns.pack(pady=20)
        
        tk.Button(frame_btns, text="¡HACERLO!", bg="#4CAF50", fg="white", font="bold", 
                  command=self.action_submit, width=12, height=2).pack(side="left", padx=10)
        
        self.btn_pass = tk.Button(frame_btns, text="PASAR", bg="#FF9800", fg="white", font="bold", 
                                  command=self.action_pass, width=12, height=2)
        self.btn_pass.pack(side="left", padx=10)

    def _get_difficulty_time(self) -> float:
        score = self.logic.score
        if score >= 100: return 3.0
        if score >= 50: return 5.0
        if score >= 25: return 7.5
        if score >= 10: return 10.0
        return 15.0

    def start_new_turn(self):
        if not self.root.winfo_exists(): return
        self.is_playing = True
        self.hurry_mode = False 

        text_display, is_simon = self.logic.generate_turn()
        self.lbl_instruction.config(text=text_display, fg="black")
        
        self.entry.delete(0, tk.END)
        self.entry.config(state='normal')
        self.entry.focus()
        
        pass_lock = Config.SETTINGS.get("gameplay", {}).get("pass_lock_ms", 500)
        self.btn_pass.config(state='disabled', bg="#cccccc") 
        self.root.after(pass_lock, self._enable_pass_button)

        self._play_turn_music()
        self.timer_val = self._get_difficulty_time()
        self._stop_timer()
        self._update_timer()

    def _play_turn_music(self):
        self.sound_manager.stop_all()
        country = self.logic.last_country
        
        if country == "España":
            self.sound_manager.play_background("special_espana")
        elif country == "Perú":
            self.sound_manager.play_background("special_peru")
        elif country == "Japón":
            self.sound_manager.play_effect("special_japon") 
            self.root.after(1500, lambda: self.sound_manager.play_background("bg_normal"))
        else:
            track = "bg_rare" if random.random() < 0.10 else "bg_normal"
            self.sound_manager.play_background(track)

    def _enable_pass_button(self):
        if self.is_playing and self.btn_pass.winfo_exists():
            self.btn_pass.config(state='normal', bg="#FF9800")

    def _update_timer(self):
        if not self.is_playing: return
        
        display_time = f"{self.timer_val:.1f}" if isinstance(self.timer_val, float) else str(self.timer_val)
        self.lbl_timer.config(text=f"⏱ {display_time}s")
        
        if self.timer_val <= 5 and not self.hurry_mode:
            self.hurry_mode = True 
            self.sound_manager.stop_all() 
            self.sound_manager.play_background("hurry")

        if self.timer_val <= 0:
            self.handle_game_over("¡SE ACABÓ EL TIEMPO!")
        else:
            self.timer_val -= 1
            self.timer_id = self.root.after(1000, self._update_timer)

    def _stop_timer(self):
        if self.timer_id:
            self.root.after_cancel(self.timer_id)
            self.timer_id = None

    def action_submit(self):
        if not self.is_playing: return
        self.sound_manager.stop_all() 
        self._stop_timer()
        success, msg = self.logic.check_answer(self.entry.get())
        self._process_result(success, msg)

    def action_pass(self):
        if not self.is_playing: return
        if self.btn_pass['state'] == 'disabled': return 
        self.sound_manager.stop_all() 
        self._stop_timer()
        success, msg = self.logic.check_pass()
        self._process_result(success, msg)

    def _process_result(self, success, fail_msg):
        self.sound_manager.stop_all()
        if success:
            self.lbl_instruction.config(text="✨ ¡CORRECTO! ✨", fg="#4CAF50")
            self.entry.delete(0, tk.END)
            self.entry.config(state='disabled')
            self.btn_pass.config(state='disabled')
            
            if self.logic.score == 15:
                self.sound_manager.play_effect("epic_15")
                messagebox.showinfo("¡INCREÍBLE!", "¡15 PUNTOS!")
            
            self.lbl_score.config(text=f"Pts: {self.logic.score}")
            self.root.after(2000, self.start_new_turn)
        else:
            sound_key = "fail_1" if random.random() < 0.5 else "fail_2"
            self.sound_manager.play_effect(sound_key)
            self.handle_game_over(fail_msg)

    def handle_game_over(self, reason):
        self.is_playing = False
        new_record = self.logic.save_record()
        
        for widget in self.game_container.winfo_children(): widget.destroy()

        tk.Label(self.game_container, text=f"💀 FIN 💀\n{reason}", 
                 font=("Helvetica", 20, "bold"), fg="red", bg=self.bg_color).pack(pady=20)
        
        msg = f"¡Récord Nuevo!: {self.logic.high_score}" if new_record else f"Puntos: {self.logic.score}"
        
        frame_over = tk.Frame(self.root, bg="#333", relief="raised", bd=5)
        frame_over.place(relx=0.5, rely=0.5, anchor="center", width=400, height=220)
        
        tk.Label(frame_over, text="¡PERDISTE!", fg="red", bg="#333", font=("Arial", 20, "bold")).pack(pady=15)
        tk.Label(frame_over, text=msg, fg="white", bg="#333", font=("Arial", 14)).pack(pady=5)
        
        tk.Button(frame_over, text="Reintentar", command=self.start_game_session, 
                  bg="white", font=("Arial", 11), width=15).pack(pady=10)
        tk.Button(frame_over, text="Salir", command=self.root.destroy, 
                  bg="#D32F2F", fg="white", font=("Arial", 11), width=15).pack(pady=5)