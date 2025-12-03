import tkinter as tk
from tkinter import messagebox
import chess
import chess.engine
import random
import os

class AjedrezApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Ajedrez Python + Stockfish Configurable")
        self.root.geometry("900x700")
        
        # --- RUTA DEL MOTOR ---
        # Si usas ruta completa, ponla aquí con r"" 
        # Ejemplo: r"C:\Users\TuUsuario\Downloads\stockfish.exe"
        self.ruta_stockfish = "stockfish.exe" 
        
        self.color_claro = "#F0D9B5"
        self.color_oscuro = "#B58863"
        self.color_resaltado = "#6A9955"
        self.pieces = {
            'r': '♜', 'n': '♞', 'b': '♝', 'q': '♛', 'k': '♚', 'p': '♟',
            'R': '♖', 'N': '♘', 'B': '♗', 'Q': '♕', 'K': '♔', 'P': '♙'
        }
        
        self.modo_juego = None 
        self.buttons = {}
        self.selected_square = None
        self.nivel_dificultad = 10 # Valor por defecto
        
        self.mostrar_menu()

    def mostrar_menu(self):
        for widget in self.root.winfo_children(): widget.destroy()
        
        menu_frame = tk.Frame(self.root)
        menu_frame.pack(expand=True)
        
        tk.Label(menu_frame, text="♞ Ajedrez Pro ♜", font=("Helvetica", 30, "bold")).pack(pady=20)
        
        # --- VERIFICACIÓN DE ENGINE ---
        estado_sf = " (No detectado)"
        color_sf = "red"
        estado_btn = "disabled" # Deshabilitar si no hay engine
        
        if os.path.exists(self.ruta_stockfish):
            estado_sf = " (Activado)"
            color_sf = "green"
            estado_btn = "normal"
        
        # --- BOTONES ---
        btn_pvp = tk.Button(menu_frame, text="Jugador vs Jugador", font=("Arial", 16), 
                            width=25, command=lambda: self.iniciar_juego("PVP"))
        btn_pvp.pack(pady=5)
        
        # Espaciador
        tk.Label(menu_frame, text="").pack()

        # --- CONTROL DE DIFICULTAD ---
        tk.Label(menu_frame, text="Nivel de la IA (0 - 20)", font=("Arial", 12)).pack()
        
        # Slider para elegir dificultad
        self.slider_dificultad = tk.Scale(menu_frame, from_=0, to=20, orient=tk.HORIZONTAL, length=300)
        self.slider_dificultad.set(5) # Valor inicial recomendado
        self.slider_dificultad.pack(pady=5)
        
        lbl_info_dif = tk.Label(menu_frame, text="(0=Fácil, 5=Intermedio, 20=Imposible)", font=("Arial", 9, "italic"))
        lbl_info_dif.pack(pady=5)

        # Botón VS CPU
        btn_cpu = tk.Button(menu_frame, text=f"Jugador vs Stockfish{estado_sf}", font=("Arial", 16), 
                            width=25, fg=color_sf, state=estado_btn,
                            command=lambda: self.iniciar_juego("CPU"))
        btn_cpu.pack(pady=10)
        
        if color_sf == "red":
            tk.Label(menu_frame, text="⚠ Coloca 'stockfish.exe' en la carpeta para activar la IA", fg="red").pack()

    def iniciar_juego(self, modo):
        self.modo_juego = modo
        # Guardamos el valor del slider
        self.nivel_actual = self.slider_dificultad.get()
        
        self.board = chess.Board()
        self.selected_square = None
        self.juego_terminado = False
        
        for widget in self.root.winfo_children(): widget.destroy()
        
        main_layout = tk.Frame(self.root)
        main_layout.pack(padx=10, pady=10, fill="both", expand=True)
        
        self.board_frame = tk.Frame(main_layout)
        self.board_frame.pack(side=tk.LEFT)
        
        self.info_frame = tk.Frame(main_layout, width=250)
        self.info_frame.pack(side=tk.RIGHT, fill="y", padx=20)
        
        tk.Button(self.info_frame, text="< Menú Principal", command=self.mostrar_menu, bg="#ffcccc").pack(fill="x", pady=5)
        
        modo_texto = f"Modo: {modo}"
        if modo == "CPU":
            modo_texto += f"\nNivel: {self.nivel_actual}/20"
            
        tk.Label(self.info_frame, text=modo_texto, font=("Arial", 12, "bold")).pack(pady=10)
        
        tk.Label(self.info_frame, text="Historial:").pack(anchor="w")
        self.history_text = tk.Text(self.info_frame, width=25, height=20, state='disabled')
        self.history_text.pack(pady=5)
        
        self.status_label = tk.Label(self.info_frame, text="Turno: Blancas", font=("Arial", 11), fg="blue")
        self.status_label.pack(pady=10)
        
        self.crear_casillas()
        self.actualizar_tablero()

    def crear_casillas(self):
        self.buttons = {}
        for fila in range(8):
            for col in range(8):
                idx = chess.square(col, 7 - fila)
                btn = tk.Button(self.board_frame, text="", font=("Arial", 28), width=2, height=1,
                                command=lambda s=idx: self.on_click(s))
                btn.grid(row=fila, column=col)
                self.buttons[idx] = btn

    def actualizar_tablero(self):
        for idx in range(64):
            piece = self.board.piece_at(idx)
            btn = self.buttons[idx]
            btn.config(text=self.pieces[piece.symbol()] if piece else "")
            
            fila = 7 - chess.square_rank(idx)
            col = chess.square_file(idx)
            color_base = self.color_claro if (fila + col) % 2 == 0 else self.color_oscuro
            
            if self.selected_square == idx:
                btn.config(bg=self.color_resaltado)
            elif self.board.is_check() and piece and piece.piece_type == chess.KING and piece.color == self.board.turn:
                 btn.config(bg="#FF5555")
            else:
                btn.config(bg=color_base)
        
        if not self.juego_terminado:
            turno = "Blancas" if self.board.turn == chess.WHITE else "Negras"
            self.status_label.config(text=f"Turno: {turno}")

    def agregar_historial(self, move_san):
        n = self.board.fullmove_number
        txt = f"{n}. {move_san} " if self.board.turn == chess.BLACK else f"{move_san}\n"
        self.history_text.config(state='normal')
        self.history_text.insert(tk.END, txt)
        self.history_text.see(tk.END)
        self.history_text.config(state='disabled')

    def on_click(self, square):
        if self.juego_terminado: return
        if self.modo_juego == "CPU" and self.board.turn == chess.BLACK: return

        if self.selected_square is None:
            piece = self.board.piece_at(square)
            if piece and piece.color == self.board.turn:
                self.selected_square = square
                self.actualizar_tablero()
        else:
            if square == self.selected_square:
                self.selected_square = None
            else:
                move = chess.Move(self.selected_square, square)
                if self.es_promocion(move): move.promotion = chess.QUEEN
                
                if move in self.board.legal_moves:
                    self.ejecutar_movimiento(move)
                    if self.modo_juego == "CPU" and not self.juego_terminado:
                        self.root.after(100, self.movimiento_ia)
                else:
                    piece = self.board.piece_at(square)
                    if piece and piece.color == self.board.turn:
                        self.selected_square = square
                    else:
                        self.selected_square = None
            self.actualizar_tablero()

    def ejecutar_movimiento(self, move):
        san = self.board.san(move)
        self.board.push(move)
        self.agregar_historial(san)
        self.selected_square = None
        self.actualizar_tablero()
        self.verificar_fin()

    def movimiento_ia(self):
        if self.juego_terminado: return
        self.status_label.config(text=f"Stockfish (Nivel {self.nivel_actual}) pensando...")
        self.root.update()

        mejor_move = None
        try:
            # Configurar motor con el nivel elegido
            with chess.engine.SimpleEngine.popen_uci(self.ruta_stockfish) as engine:
                # AQUÍ ESTÁ LA MAGIA: Configuramos "Skill Level"
                engine.configure({"Skill Level": self.nivel_actual})
                
                # Tiempo de pensamiento: Reducido para niveles bajos, mayor para altos
                tiempo = 0.1 if self.nivel_actual < 5 else 0.5
                
                result = engine.play(self.board, chess.engine.Limit(time=tiempo))
                mejor_move = result.move
        except Exception as e:
            print(f"Error engine: {e}")
            # Fallback a random si falla
            moves = list(self.board.legal_moves)
            mejor_move = random.choice(moves)

        self.ejecutar_movimiento(mejor_move)

    def es_promocion(self, move):
        p = self.board.piece_at(move.from_square)
        if p and p.piece_type == chess.PAWN:
            rank = chess.square_rank(move.to_square)
            if (p.color == chess.WHITE and rank == 7) or (p.color == chess.BLACK and rank == 0):
                return True
        return False

    def verificar_fin(self):
        if self.board.is_game_over():
            self.juego_terminado = True
            res = self.board.result()
            winner = "Nadie"
            if self.board.is_checkmate():
                winner = "Negras" if self.board.turn == chess.WHITE else "Blancas"
                msg = f"¡Jaque Mate! Ganan: {winner}"
            else:
                msg = "Tablas / Empate"
            messagebox.showinfo("Fin", f"{msg}\nResultado: {res}")

if __name__ == "__main__":
    root = tk.Tk()
    app = AjedrezApp(root)
    root.mainloop()