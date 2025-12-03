import math
import random
import sys
import pygame
from typing import List, Tuple, Optional

# --- CONFIGURACIÓN Y CONSTANTES ---

class Config:
    """Configuración general del juego"""
    WIDTH: int = 900
    HEIGHT: int = 600
    FPS: int = 60
    GRAVITY: float = 9.81 * 100  # px/s^2 ajustada a escala visual
    TITLE: str = "Juego del Cañón - Prototipo Refactorizado"

class Colors:
    """Paleta de colores"""
    BACKGROUND = (135, 206, 235)  # Sky Blue
    GROUND = (85, 170, 60)        # Grass Green
    TEXT = (10, 10, 10)
    CANNON = (80, 80, 80)
    PROJECTILE = (200, 50, 50)
    PROJECTILE_TRAIL = (150, 150, 150)
    TARGET = (50, 180, 50)
    TARGET_CENTER = (255, 255, 255)
    PREDICTION_LINE = (0, 0, 0)
    MESSAGE_SUCCESS = (255, 40, 40)

class PhysicsParams:
    """Parámetros físicos por defecto"""
    PROJECTILE_RADIUS = 6
    TARGET_RADIUS = 20
    DRAG_COEFF = 0.02
    CANNON_LENGTH = 40
    CANNON_POS = (60, Config.HEIGHT - 60)

# --- UTILIDADES ---

def clamp(value: float, min_val: float, max_val: float) -> float:
    return max(min_val, min(max_val, value))

# --- CLASES DEL JUEGO ---

class Projectile:
    def __init__(self, x: float, y: float, vx: float, vy: float):
        self.x = x
        self.y = y
        self.vx = vx
        self.vy = vy
        self.radius = PhysicsParams.PROJECTILE_RADIUS
        self.alive = True
        self.trail: List[Tuple[int, int]] = []

    def update(self, dt: float, wind_accel: float, drag_enabled: bool) -> None:
        """Calcula la nueva posición basada en velocidad, gravedad, viento y rozamiento."""
        ax = wind_accel
        ay = Config.GRAVITY

        if drag_enabled:
            ax -= PhysicsParams.DRAG_COEFF * self.vx
            ay -= PhysicsParams.DRAG_COEFF * self.vy

        self.vx += ax * dt
        self.vy += ay * dt
        self.x += self.vx * dt
        self.y += self.vy * dt

        # Guardar estela
        self.trail.append((int(self.x), int(self.y)))
        if len(self.trail) > 300:
            self.trail.pop(0)

        # Verificar límites de pantalla
        if (self.y - self.radius > Config.HEIGHT or 
            self.x - self.radius > Config.WIDTH or 
            self.x + self.radius < 0):
            self.alive = False

    def draw(self, surface: pygame.Surface, show_trail: bool) -> None:
        if show_trail and len(self.trail) > 1:
            # Dibujar estela optimizada (saltando puntos para rendimiento)
            if len(self.trail) >= 2:
                pygame.draw.lines(surface, Colors.PROJECTILE_TRAIL, False, self.trail, 2)
        
        pygame.draw.circle(surface, Colors.PROJECTILE, (int(self.x), int(self.y)), self.radius)


class Target:
    def __init__(self, x: float, y: float, mobile: bool = False):
        self.base_x = x
        self.x = x
        self.y = y
        self.radius = PhysicsParams.TARGET_RADIUS
        self.mobile = mobile
        self.time_elapsed = 0.0
        self.amplitude = random.uniform(50, 150)
        self.speed = random.uniform(0.6, 1.6)

    def update(self, dt: float) -> None:
        if self.mobile:
            self.time_elapsed += dt
            self.x = self.base_x + math.sin(self.time_elapsed * self.speed) * self.amplitude

    def draw(self, surface: pygame.Surface) -> None:
        pos = (int(self.x), int(self.y))
        pygame.draw.circle(surface, Colors.TARGET, pos, self.radius)
        pygame.draw.circle(surface, Colors.TARGET_CENTER, pos, int(self.radius * 0.4))

    def check_collision(self, proj: Projectile) -> bool:
        dx = self.x - proj.x
        dy = self.y - proj.y
        dist_sq = dx*dx + dy*dy
        return dist_sq <= (self.radius + proj.radius)**2


class GameManager:
    def __init__(self):
        # Inicialización de Pygame segura
        status = pygame.init()
        if status[1] > 0:
            print(f"Advertencia: {status[1]} módulos de Pygame fallaron al iniciar.")

        self.screen = pygame.display.set_mode((Config.WIDTH, Config.HEIGHT))
        pygame.display.set_caption(Config.TITLE)
        self.clock = pygame.time.Clock()
        
        # Fuentes
        try:
            self.font_ui = pygame.font.SysFont("Arial", 18)
            self.font_msg = pygame.font.SysFont("Arial", 48, bold=True)
        except Exception as e:
            print(f"Error cargando fuentes: {e}, usando fuente por defecto.")
            self.font_ui = pygame.font.Font(None, 24)
            self.font_msg = pygame.font.Font(None, 48)

        # Estado del juego
        self.running = True
        self.score = 0
        self.angle = 35.0
        self.power = 400.0
        self.message = ""
        self.message_timer = 0.0
        
        # Flags de física
        self.enable_wind = False
        self.enable_drag = False
        self.show_trail = True
        self.mobile_target_enabled = True
        self.wind_accel = 0.0

        # Objetos
        self.projectile: Optional[Projectile] = None
        self.target = self._create_target()

    def _create_target(self) -> Target:
        """Crea un nuevo objetivo en una posición aleatoria segura."""
        x_pos = random.randint(500, Config.WIDTH - 80)
        return Target(x_pos, Config.HEIGHT - 120, mobile=self.mobile_target_enabled)

    def handle_input(self, dt: float) -> None:
        """Maneja eventos y estado del teclado."""
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
            elif event.type == pygame.KEYDOWN:
                self._handle_keydown(event)

        # Input continuo (mantener tecla)
        keys = pygame.key.get_pressed()
        if keys[pygame.K_UP]: 
            self.angle = clamp(self.angle + 60 * dt, 0, 85)
        if keys[pygame.K_DOWN]: 
            self.angle = clamp(self.angle - 60 * dt, 0, 85)
        if keys[pygame.K_RIGHT]: 
            self.power = clamp(self.power + 200 * dt, 50, 1200)
        if keys[pygame.K_LEFT]: 
            self.power = clamp(self.power - 200 * dt, 50, 1200)

    def _handle_keydown(self, event):
        """Maneja pulsaciones individuales."""
        if event.key == pygame.K_SPACE and self.projectile is None:
            self._fire_projectile()
        elif event.key == pygame.K_r:
            self._reset_round()
        elif event.key == pygame.K_m:
            self.mobile_target_enabled = not self.mobile_target_enabled
            self.target.mobile = self.mobile_target_enabled
        elif event.key == pygame.K_w:
            self.enable_wind = not self.enable_wind
            self.wind_accel = random.uniform(-200, 200) if self.enable_wind else 0.0
        elif event.key == pygame.K_a:
            self.enable_drag = not self.enable_drag
        elif event.key == pygame.K_t:
            self.show_trail = not self.show_trail
        elif event.key == pygame.K_ESCAPE:
            self.running = False

    def _fire_projectile(self):
        rad = math.radians(self.angle)
        # Posición inicial (punta del cañón)
        cx, cy = PhysicsParams.CANNON_POS
        length = PhysicsParams.CANNON_LENGTH
        start_x = cx + length * math.cos(rad)
        start_y = cy - length * math.sin(rad)
        
        # Velocidad inicial
        vx = math.cos(rad) * self.power
        vy = -math.sin(rad) * self.power
        
        self.projectile = Projectile(start_x, start_y, vx, vy)

    def _reset_round(self):
        self.projectile = None
        self.target = self._create_target()
        self.message = ""

    def update(self, dt: float) -> None:
        """Actualiza la lógica del juego."""
        self.target.update(dt)

        if self.projectile:
            wind = self.wind_accel if self.enable_wind else 0.0
            self.projectile.update(dt, wind, self.enable_drag)
            
            if self.target.check_collision(self.projectile):
                self.message = "¡Has acertado!"
                self.message_timer = 2.0
                self.score += 1
                self.projectile.alive = False
            
            if not self.projectile.alive:
                self.projectile = None

        if self.message_timer > 0:
            self.message_timer -= dt
            if self.message_timer <= 0:
                self.message = ""

    def _draw_prediction_line(self):
        """Dibuja la trayectoria predicha."""
        rad = math.radians(self.angle)
        cx, cy = PhysicsParams.CANNON_POS
        sim_x = cx + PhysicsParams.CANNON_LENGTH * math.cos(rad)
        sim_y = cy - PhysicsParams.CANNON_LENGTH * math.sin(rad)
        sim_vx = math.cos(rad) * self.power
        sim_vy = -math.sin(rad) * self.power
        
        sim_dt = 0.03
        points = []
        
        # Simulación de física simplificada (Euler)
        steps = 60 # Cantidad de puntos a predecir
        wind = self.wind_accel if self.enable_wind else 0.0

        for _ in range(steps):
            ax = wind
            ay = Config.GRAVITY
            
            if self.enable_drag:
                ax -= PhysicsParams.DRAG_COEFF * sim_vx
                ay -= PhysicsParams.DRAG_COEFF * sim_vy
            
            sim_vx += ax * sim_dt
            sim_vy += ay * sim_dt
            sim_x += sim_vx * sim_dt
            sim_y += sim_vy * sim_dt
            
            if sim_y > Config.HEIGHT - 50: # Detener si toca el suelo
                break
            points.append((int(sim_x), int(sim_y)))

        if len(points) > 1:
            # Dibujar línea punteada manualmente (Pygame no tiene soporte nativo para dotted lines fácil)
            for i in range(0, len(points) - 1, 4):
                if i+1 < len(points):
                    pygame.draw.line(self.screen, Colors.PREDICTION_LINE, points[i], points[i+1], 1)

    def draw(self) -> None:
        """Renderiza todos los elementos en pantalla."""
        self.screen.fill(Colors.BACKGROUND)
        
        # Suelo
        pygame.draw.rect(self.screen, Colors.GROUND, (0, Config.HEIGHT - 60, Config.WIDTH, 60))

        # Cañón
        rad = math.radians(self.angle)
        cx, cy = PhysicsParams.CANNON_POS
        end_x = cx + PhysicsParams.CANNON_LENGTH * math.cos(rad)
        end_y = cy - PhysicsParams.CANNON_LENGTH * math.sin(rad)
        
        pygame.draw.circle(self.screen, Colors.CANNON, (cx, cy), 22)
        pygame.draw.line(self.screen, Colors.CANNON, (cx, cy), (end_x, end_y), 8)

        # Objetos
        self._draw_prediction_line()
        self.target.draw(self.screen)
        
        if self.projectile:
            self.projectile.draw(self.screen, self.show_trail)

        # UI / HUD
        self._draw_ui()

        pygame.display.flip()

    def _draw_ui(self):
        # Texto de ayuda (Controles)
        controls = [
            "CONTROLES (ESC: Salir):", 
            "M: Diana móvil", 
            "W: Viento", 
            "A: Rozamiento", 
            "T: Estela"
        ]
        
        for i, line in enumerate(controls):
            surf = self.font_ui.render(line, True, Colors.TEXT)
            self.screen.blit(surf, (10, 60 + i * 20))

        # Texto de estado
        status_text_1 = f"Ángulo: {self.angle:.1f}° | Potencia: {self.power:.0f} | Puntuación: {self.score}"
        wind_status = f"Viento: {'ON' if self.enable_wind else 'OFF'} ({self.wind_accel:.1f})"
        drag_status = f"Rozamiento: {'ON' if self.enable_drag else 'OFF'}"
        mobile_status = f"Diana Móvil: {'ON' if self.mobile_target_enabled else 'OFF'}"
        
        status_text_2 = f"{wind_status} | {drag_status} | {mobile_status}"

        surf1 = self.font_ui.render(status_text_1, True, Colors.TEXT)
        surf2 = self.font_ui.render(status_text_2, True, Colors.TEXT)
        
        self.screen.blit(surf1, (10, 10))
        self.screen.blit(surf2, (10, 32))

        # Mensaje central
        if self.message:
            msg_surf = self.font_msg.render(self.message, True, Colors.MESSAGE_SUCCESS)
            rect = msg_surf.get_rect(center=(Config.WIDTH // 2, 80))
            self.screen.blit(msg_surf, rect)

    def run(self):
        """Bucle principal del juego."""
        while self.running:
            dt = self.clock.tick(Config.FPS) / 1000.0  # Delta time en segundos
            self.handle_input(dt)
            self.update(dt)
            self.draw()
        
        pygame.quit()
        sys.exit()

# --- ENTRY POINT ---

if __name__ == '__main__':
    try:
        game = GameManager()
        game.run()
    except Exception as e:
        print(f"Ocurrió un error fatal: {e}")
        pygame.quit()
        sys.exit(1)
    except KeyboardInterrupt:
        print("\nJuego cerrado por el usuario.")
        pygame.quit()
        sys.exit(0)