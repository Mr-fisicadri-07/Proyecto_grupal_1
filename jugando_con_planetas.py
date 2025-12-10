import turtle
import math
from typing import List
from collections import deque

# --- CONSTANTES DE CONFIGURACIÓN Y FÍSICA ---
ANCHO_PANTALLA = 1000
ALTO_PANTALLA = 800

# Factores de escala
ESCALA_DISTANCIA = 250  # 1 AU = 250 píxeles
ESCALA_MASA = 1e-4      # Factor para que las masas no sean números astronómicos gigantes en el código

# Física
G = 0.5   # Constante gravitacional visual
DT = 0.02 # Delta time (paso de tiempo)

# Configuración de rastros
LONGITUD_RASTRO = 100  # Reducido ligeramente para mejorar rendimiento
INTERVALO_RASTRO = 3   # Solo guardar posición cada X frames para suavizar y optimizar

class CuerpoCeleste:
    def __init__(self, nombre: str, masa_relativa: float, dist_au: float, color: str, radio_visual: float, es_estatico: bool = False):
        self.nombre = nombre
        self.masa = masa_relativa * ESCALA_MASA
        self.es_estatico = es_estatico # Nueva propiedad para fijar el Sol
        
        # Posición inicial
        self.distancia_inicial = dist_au * ESCALA_DISTANCIA
        self.x = self.distancia_inicial
        self.y = 0
        
        # Velocidad inicial (se calculará automáticamente si no es estático)
        self.vx = 0
        self.vy = 0 
        
        self.color = color
        self.radio_visual = radio_visual
        
        # Historial de posiciones
        self.historial_pos = deque(maxlen=LONGITUD_RASTRO)
        self.contador_rastro = 0

        # --- Elementos Gráficos ---
        self.t_cuerpo = turtle.Turtle()
        self.t_cuerpo.shape("circle")
        self.t_cuerpo.color(color)
        # Ajustamos el tamaño base de la tortuga (por defecto es 20x20px)
        self.t_cuerpo.shapesize(radio_visual / 10)
        self.t_cuerpo.penup()
        
        self.t_rastro = turtle.Turtle()
        self.t_rastro.hideturtle()
        self.t_rastro.color(color)
        self.t_rastro.pensize(1)
        self.t_rastro.penup()

    def calcular_velocidad_orbital_circular(self, cuerpo_central: 'CuerpoCeleste'):
        """
        Calcula la velocidad necesaria para mantener una órbita circular perfecta
        alrededor de un cuerpo central masivo.
        Fórmula: v = raiz( (G * M) / r )
        """
        if self.es_estatico or self.distancia_inicial == 0:
            return

        # Distancia r
        r = abs(self.x - cuerpo_central.x)
        
        # Velocidad necesaria: v = sqrt(GM/r)
        # Nota: Asumimos que la masa del cuerpo central domina el sistema
        velocidad = math.sqrt((G * cuerpo_central.masa) / r)
        
        # Como el planeta empieza a la derecha (eje X), la velocidad debe ser hacia arriba (eje Y)
        # Si la órbita fuera en sentido horario, sería negativo.
        self.vy = velocidad

    def calcular_fuerzas(self, otros_cuerpos: List['CuerpoCeleste']):
        """Calcula la aceleración resultante."""
        if self.es_estatico: 
            return # Si es el Sol fijo, no calculamos fuerzas sobre él

        fx_total = 0
        fy_total = 0
        
        for otro in otros_cuerpos:
            if self == otro: continue
            
            dx = otro.x - self.x
            dy = otro.y - self.y
            distancia_sq = dx**2 + dy**2
            distancia = math.sqrt(distancia_sq)

            if distancia < 5: continue # Evitar colapso si chocan

            # F = G * m1 * m2 / r^2
            fuerza = (G * self.masa * otro.masa) / distancia_sq
            
            # Descomposición vectorial
            fx_total += fuerza * (dx / distancia)
            fy_total += fuerza * (dy / distancia)
            
        # a = F / m
        self.ax = fx_total / self.masa
        self.ay = fy_total / self.masa

    def actualizar_fisica(self):
        if self.es_estatico: 
            return

        # Método de Euler semi-implícito (ligeramente más estable que Euler simple)
        self.vx += self.ax * DT
        self.vy += self.ay * DT
        self.x += self.vx * DT
        self.y += self.vy * DT
        
        # Gestión optimizada del rastro
        self.contador_rastro += 1
        if self.contador_rastro >= INTERVALO_RASTRO:
            self.historial_pos.append((self.x, self.y))
            self.contador_rastro = 0

    def dibujar(self, cam_x, cam_y, zoom):
        # 1. Dibujar Rastro (Transformado por cámara)
        self.t_rastro.clear()
        
        # Solo dibujamos si hay suficientes puntos y si el cuerpo no es estático (el Sol no necesita rastro)
        if len(self.historial_pos) > 1 and not self.es_estatico:
            # Movemos al primer punto sin pintar
            wx0, wy0 = self.historial_pos[0]
            self.t_rastro.goto((wx0 - cam_x) * zoom, (wy0 - cam_y) * zoom)
            self.t_rastro.pendown()
            
            # Pintamos el resto
            for wx, wy in self.historial_pos:
                screen_x = (wx - cam_x) * zoom
                screen_y = (wy - cam_y) * zoom
                self.t_rastro.goto(screen_x, screen_y)
            
            self.t_rastro.penup()

        # 2. Dibujar Cuerpo
        screen_x = (self.x - cam_x) * zoom
        screen_y = (self.y - cam_y) * zoom
        self.t_cuerpo.goto(screen_x, screen_y)
        
        # Efecto visual: escalar el tamaño del planeta con el zoom
        # (Limitado para que no desaparezcan si hacemos mucho zoom out)
        nuevo_tamano = (self.radio_visual / 10) * zoom
        if nuevo_tamano < 0.2: nuevo_tamano = 0.2
        self.t_cuerpo.shapesize(nuevo_tamano)

class SistemaSolar:
    def __init__(self):
        self.cuerpos: List[CuerpoCeleste] = []
        self.pantalla = turtle.Screen()
        self._configurar_pantalla()
        
        self.cam_x = 0
        self.cam_y = 0
        self.zoom = 0.8
        self._configurar_controles()
        
        self.corriendo = True

    def _configurar_pantalla(self):
        self.pantalla.setup(ANCHO_PANTALLA, ALTO_PANTALLA)
        self.pantalla.bgcolor("#050510")
        self.pantalla.title("Simulación Gravitatoria N-Cuerpos")
        self.pantalla.tracer(0)

    def _configurar_controles(self):
        # Velocidad de paneo ajustada al zoom actual
        def mover(dx, dy):
            self.cam_x += dx / self.zoom
            self.cam_y += dy / self.zoom

        self.pantalla.listen()
        self.pantalla.onkeypress(lambda: mover(0, 50), "Up")
        self.pantalla.onkeypress(lambda: mover(0, -50), "Down")
        self.pantalla.onkeypress(lambda: mover(-50, 0), "Left")
        self.pantalla.onkeypress(lambda: mover(50, 0), "Right")
        
        def zoom(factor): self.zoom *= factor
        self.pantalla.onkeypress(lambda: zoom(1.1), "plus")
        self.pantalla.onkeypress(lambda: zoom(1.1), "w")
        self.pantalla.onkeypress(lambda: zoom(0.9), "minus")
        self.pantalla.onkeypress(lambda: zoom(0.9), "s")
        
        self.pantalla.onkeypress(lambda: setattr(self, 'corriendo', False), "Escape")

    def agregar_cuerpo(self, cuerpo: CuerpoCeleste):
        self.cuerpos.append(cuerpo)

    def inicializar_orbitas(self):
        """Calcula velocidades automáticas basándose en el cuerpo más masivo (el Sol)"""
        # Buscamos el cuerpo con más masa para que sea el centro de gravedad
        cuerpo_masivo = max(self.cuerpos, key=lambda c: c.masa)
        
        for cuerpo in self.cuerpos:
            if cuerpo != cuerpo_masivo:
                cuerpo.calcular_velocidad_orbital_circular(cuerpo_masivo)

    def paso_simulacion(self):
        # 1. Física
        for cuerpo in self.cuerpos:
            cuerpo.calcular_fuerzas(self.cuerpos)
        
        for cuerpo in self.cuerpos:
            cuerpo.actualizar_fisica()
            
        # 2. Renderizado
        for cuerpo in self.cuerpos:
            cuerpo.dibujar(self.cam_x, self.cam_y, self.zoom)
            
        self.pantalla.update()

    def ejecutar(self):
        self.inicializar_orbitas() # ¡Importante! Calcular velocidades antes de empezar
        try:
            while self.corriendo:
                self.paso_simulacion()
        except turtle.Terminator:
            pass

if __name__ == "__main__":
    sistema = SistemaSolar()

    # --- Configuración de Cuerpos ---
    # Nota: Ya no pasamos vel_inicial manual. Se calcula sola.
    
    # El Sol (Estático para evitar que 'vague' por la pantalla)
    sol = CuerpoCeleste("Sol", masa_relativa=330000, dist_au=0, color="yellow", radio_visual=40, es_estatico=True)
    
    mercurio = CuerpoCeleste("Mercurio", masa_relativa=0.055, dist_au=0.39, color="gray", radio_visual=6)
    venus = CuerpoCeleste("Venus", masa_relativa=0.815, dist_au=0.72, color="orange", radio_visual=10)
    tierra = CuerpoCeleste("Tierra", masa_relativa=1.0, dist_au=1.0, color="blue", radio_visual=11)
    marte = CuerpoCeleste("Marte", masa_relativa=0.107, dist_au=1.52, color="red", radio_visual=8)
    jupiter = CuerpoCeleste("Júpiter", masa_relativa=317.8, dist_au=5.2, color="brown", radio_visual=28)

    # Agregamos cuerpos
    sistema.agregar_cuerpo(sol)
    sistema.agregar_cuerpo(mercurio)
    sistema.agregar_cuerpo(venus)
    sistema.agregar_cuerpo(tierra)
    sistema.agregar_cuerpo(marte)
    sistema.agregar_cuerpo(jupiter)
    
    # Ajuste inicial de cámara
    sistema.zoom = 0.5
    
    sistema.ejecutar()