import tkinter as tk
from tkinter import messagebox
import random
import os
import threading
import sys

# Intentamos importar winsound solo si estamos en Windows
try:
    import winsound
    TIENE_SONIDO = True
except ImportError:
    TIENE_SONIDO = False  # En Mac/Linux funcionará sin sonido

class SimonDiceApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Simón Dice - Edición Sonora")
        self.root.geometry("500x520")
        self.root.configure(bg="#f0f0f0")

        # --- CONFIGURACIÓN DE PERSISTENCIA ---
        # self.archivo_record = "simon_record.txt"
        # self.record_maximo = self.cargar_record()

        # --- PROTOCOLO DE CIERRE ---
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)

        # Variables del juego
        self.puntuacion = 0
        self.respuesta_correcta = ""
        self.simon_lo_dijo = False
        self.jugando = True
        
        # Variables del Temporizador
        self.tiempo_limite = 15
        self.tiempo_restante = self.tiempo_limite
        self.timer_id = None 

        # --- INTERFAZ GRÁFICA ---
        try:
            self.crear_interfaz()
        except Exception as e:
            messagebox.showerror("Error Crítico", f"No se pudo cargar la interfaz: {e}")
            self.root.destroy()

        self.nuevo_turno()

    # ---------------------------------------------------------
    #               SISTEMA DE SONIDOS (NUEVO)
    # ---------------------------------------------------------
    def reproducir_sonido(self, tipo):
        """Ejecuta el sonido en un hilo separado para no congelar el juego"""
        if not TIENE_SONIDO:
            return # Si no es Windows, no hacemos nada

        # Creamos un hilo para que el Beep no detenga la interfaz
        hilo_sonido = threading.Thread(target=self._generar_tono, args=(tipo,))
        hilo_sonido.daemon = True # El hilo muere si cierras el programa
        hilo_sonido.start()

    def _generar_tono(self, tipo):
        """Genera frecuencias matemáticas"""
        try:
            if tipo == "acierto":
                # Un sonido agudo y rápido (1000 Hz por 150ms)
                winsound.Beep(1000, 150)
            elif tipo == "error":
                # Un sonido grave y largo (150 Hz por 600ms)
                winsound.Beep(150, 600)
        except Exception:
            pass

    # ---------------------------------------------------------

    def cargar_record(self):
        if not os.path.exists(self.archivo_record): return 0
        try:
            with open(self.archivo_record, "r") as f:
                c = f.read().strip()
                return int(c) if c.isdigit() else 0
        except: return 0

    def guardar_record(self):
        try:
            with open(self.archivo_record, "w") as f:
                f.write(str(self.record_maximo))
        except: pass

    def crear_interfaz(self):
        frame_info = tk.Frame(self.root, bg="#f0f0f0")
        frame_info.pack(pady=10)

        self.label_record = tk.Label(frame_info, text=f"🏆 Récord: {self.record_maximo}", font=("Arial", 12, "bold"), fg="#FF9800", bg="#f0f0f0")
        self.label_record.pack(side=tk.LEFT, padx=20)

        self.label_score = tk.Label(frame_info, text="Puntos: 0", font=("Arial", 12), bg="#f0f0f0")
        self.label_score.pack(side=tk.LEFT, padx=20)

        self.label_timer = tk.Label(self.root, text=f"Tiempo: {self.tiempo_limite}", font=("Arial", 14, "bold"), fg="red", bg="#f0f0f0")
        self.label_timer.pack(pady=5)

        self.label_orden = tk.Label(self.root, text="Presiona Iniciar", font=("Arial", 16, "bold"), wraplength=480, bg="#f0f0f0", fg="#333")
        self.label_orden.pack(pady=20)

        self.entry_respuesta = tk.Entry(self.root, font=("Arial", 14), width=20)
        self.entry_respuesta.pack(pady=10)
        self.root.bind('<Return>', lambda event: self.verificar_accion())

        frame_botones = tk.Frame(self.root, bg="#f0f0f0")
        frame_botones.pack(pady=20)

        self.btn_accion = tk.Button(frame_botones, text="¡Hacerlo!", command=self.verificar_accion, bg="#4CAF50", fg="white", font=("Arial", 12), width=15)
        self.btn_accion.pack(side=tk.LEFT, padx=10)

        self.btn_pasar = tk.Button(frame_botones, text="Pasar", command=self.verificar_pasar, bg="#FF5722", fg="white", font=("Arial", 12), width=15)
        self.btn_pasar.pack(side=tk.LEFT, padx=10)

        self.btn_reiniciar = tk.Button(self.root, text="Reiniciar Juego", command=self.reiniciar_juego, state=tk.DISABLED)
        self.btn_reiniciar.pack(pady=10)

    def iniciar_cuenta_regresiva(self):
        self.detener_reloj()
        self.tiempo_restante = self.tiempo_limite
        self.actualizar_reloj()

    def actualizar_reloj(self):
        if not self.jugando: return
        try:
            self.label_timer.config(text=f"Tiempo: {self.tiempo_restante} s")
            if self.tiempo_restante <= 0:
                self.reproducir_sonido("error") # SONIDO ERROR
                self.game_over("¡SE ACABÓ EL TIEMPO! Lento...")
            else:
                self.tiempo_restante -= 1
                self.timer_id = self.root.after(1000, self.actualizar_reloj)
        except tk.TclError:
            self.detener_reloj()

    def detener_reloj(self):
        if self.timer_id:
            try:
                self.root.after_cancel(self.timer_id)
            except ValueError: pass
            self.timer_id = None

    def on_closing(self):
        self.jugando = False
        self.detener_reloj()
        self.root.destroy()

    def nuevo_turno(self):
        try:
            if not self.root.winfo_exists(): return
        except tk.TclError: return
        if not self.jugando: return

        self.entry_respuesta.delete(0, tk.END)
        self.entry_respuesta.focus()

        try:
            capitales = {"francia": "paris", "españa": "madrid", "italia": "roma", "alemania": "berlin", "portugal": "lisboa", "reino unido": "londres"}
            palabras = ["python", "codigo", "simon", "juego", "ventana", "teclado"]

            tipo = random.choice(['suma', 'palabra', 'capital'])
            texto_base = ""
            
            if tipo == 'suma':
                a, b = random.randint(1, 15), random.randint(1, 15)
                texto_base = f"calcula {a} + {b}"
                self.respuesta_correcta = str(a + b)
            elif tipo == 'palabra':
                word = random.choice(palabras)
                texto_base = f"escribe '{word}'"
                self.respuesta_correcta = word
            elif tipo == 'capital':
                pais, capital = random.choice(list(capitales.items()))
                texto_base = f"¿capital de {pais.capitalize()}?"
                self.respuesta_correcta = capital

            self.simon_lo_dijo = random.choice([True, False])

            if self.simon_lo_dijo:
                self.label_orden.config(text=f"Simón dice: {texto_base}", fg="black")
            else:
                self.label_orden.config(text=f"{texto_base.capitalize()}", fg="black")

            self.iniciar_cuenta_regresiva()
        except Exception as e:
            print(f"Error: {e}")
            self.nuevo_turno()

    def verificar_accion(self):
        if not self.jugando: return
        self.detener_reloj()
        try:
            respuesta = self.entry_respuesta.get().lower().strip()
        except tk.TclError: return

        if self.simon_lo_dijo:
            if respuesta == self.respuesta_correcta:
                self.reproducir_sonido("acierto") # SONIDO ACIERTO
                self.puntuacion += 1
                self.actualizar_puntuacion()
                self.nuevo_turno()
            else:
                self.reproducir_sonido("error") # SONIDO ERROR
                msg = f"¡Mal! Era '{self.respuesta_correcta}'." if respuesta else "¡No escribiste nada!"
                self.game_over(msg)
        else:
            self.reproducir_sonido("error") # SONIDO ERROR
            self.game_over("¡Simón no dijo nada!")

    def verificar_pasar(self):
        if not self.jugando: return
        self.detener_reloj()

        if self.simon_lo_dijo:
            self.reproducir_sonido("error") # SONIDO ERROR
            self.game_over("¡Error! Simón lo dijo.")
        else:
            self.reproducir_sonido("acierto") # SONIDO ACIERTO
            self.puntuacion += 1
            self.actualizar_puntuacion()
            self.nuevo_turno()

    def actualizar_puntuacion(self):
        try:
            self.label_score.config(text=f"Puntos: {self.puntuacion}")
        except tk.TclError: pass

    def game_over(self, mensaje):
        self.jugando = False
        self.detener_reloj()
        
        es_nuevo_record = False
        if self.puntuacion > self.record_maximo:
            self.record_maximo = self.puntuacion
            self.guardar_record()
            es_nuevo_record = True
            try:
                self.label_record.config(text=f"🏆 Récord: {self.record_maximo}")
            except tk.TclError: pass

        titulo = "¡NUEVO RÉCORD!" if es_nuevo_record else "Perdiste"
        extra_msg = "¡Felicidades!" if es_nuevo_record else ""
        
        try:
            self.label_orden.config(text=f"FIN DEL JUEGO\n{mensaje}", fg="red")
            messagebox.showinfo(titulo, f"{mensaje}\n{extra_msg}\nPuntuación final: {self.puntuacion}")
            
            self.btn_accion.config(state=tk.DISABLED)
            self.btn_pasar.config(state=tk.DISABLED)
            self.btn_reiniciar.config(state=tk.NORMAL)
        except tk.TclError: pass

    def reiniciar_juego(self):
        try:
            self.puntuacion = 0
            self.jugando = True
            self.actualizar_puntuacion()
            self.btn_accion.config(state=tk.NORMAL)
            self.btn_pasar.config(state=tk.NORMAL)
            self.btn_reiniciar.config(state=tk.DISABLED)
            self.nuevo_turno()
        except tk.TclError: pass

if __name__ == "__main__":
    try:
        root = tk.Tk()
        app = SimonDiceApp(root)
        root.mainloop()
    except KeyboardInterrupt: pass