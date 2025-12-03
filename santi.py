"""
Juego del Cañón — Prototipo en Python (Pygame)

Contenido del archivo:
- Explicación paso a paso del flujo del juego.
- Diagrama simple de la escena (ASCII).
- Distribución de tareas para un equipo pequeño.
- Estructura del código.
- Prototipo completo en Pygame ejecutable.

Requisitos:
- Python 3.8+
- pygame (`pip install pygame`)

Controles:
- Flechas ARRIBA/ABAJO: ajustar ángulo del cañón (grados).
- Flechas DERECHA/IZQUIERDA: ajustar velocidad inicial (potencia).
- Barra ESPACIADORA: disparar.
- R: reiniciar bala/objetivo.
- M: alternar diana móvil.
- W: alternar viento.
- A: alternar rozamiento del aire (drag).
- T: alternar estela de la trayectoria.

Flujo del juego:
1) El jugador ve el cañón en la parte izquierda de la pantalla.
2) Ajusta ángulo y velocidad inicial con las teclas.
3) Pulsa ESPACIO para disparar: el programa inicia el temporizador del disparo.
4) Cada frame (~1/60 s) se calcula la posición del proyectil usando física (velocidad, gravedad, opcional: viento y drag).
5) Se dibuja el proyectil y (opcional) la estela completa.
6) La pelota sigue su trayectoria parabólica hasta que: toca el suelo, sale de la pantalla, o golpea la diana/obstáculo.
7) Si acierta → mostrar mensaje "¡Has acertado!" y aumentar puntuación si aplica.

Diagrama simple (ASCII):
+-----------------------------------------------+
|                                               |
|                 diana (target)                 |
|                                               |
|                                               |
|                                               |
|  CAÑÓN (izq) -> o===>                          |
|                                               |
+-----------------------------------------------+

Distribución de tareas:
- Física y motor de actualización: implementar física (gravedad, viento, drag) y colisiones.
- Gráficos y UI: dibujar cañón, proyectil, dianas, efectos, HUD.
- Niveles y diseño: posiciones de dianas, niveles, obstáculos.
- Extras y pulido: sonido, animaciones, menús, guardado de puntuaciones.

--- PROTOTIPO (PYGAME) ---
"""

import math
import random
import pygame

# ----- CONFIG -----
WIDTH, HEIGHT = 900, 600
FPS = 60
GRAVITY = 9.81 * 100  # px/s^2

# Projectile settings
PROJECTILE_RADIUS = 6
PROJECTILE_COLOR = (200, 50, 50)

# Cannon settings
CANNON_POS = (60, HEIGHT - 60)
CANNON_LENGTH = 40
CANNON_COLOR = (80, 80, 80)

# Target settings
TARGET_RADIUS = 20
TARGET_COLOR = (50, 180, 50)

# Physics toggles defaults
ENABLE_WIND = False
ENABLE_DRAG = False
SHOW_TRAIL = True
MOBILE_TARGET = True

# Wind
WIND_ACCEL = 0.0

# Drag coefficient
DRAG_COEFF = 0.02

# Utility
def clamp(x, a, b):
    return max(a, min(b, x))

# Classes
class Projectile:
    def __init__(self, pos, vel):
        self.x, self.y = pos
        self.vx, self.vy = vel
        self.radius = PROJECTILE_RADIUS
        self.alive = True
        self.trail = []

    def update(self, dt, wind_ax=0.0, drag=False):
        ax = wind_ax
        ay = GRAVITY
        if drag:
            ax -= DRAG_COEFF * self.vx
            ay -= DRAG_COEFF * self.vy
        self.vx += ax * dt
        self.vy += ay * dt
        self.x += self.vx * dt
        self.y += self.vy * dt
        self.trail.append((int(self.x), int(self.y)))
        if len(self.trail) > 300:
            self.trail.pop(0)
        if self.y - self.radius > HEIGHT or self.x - self.radius > WIDTH or self.x + self.radius < 0:
            self.alive = False

    def draw(self, surf):
        if SHOW_TRAIL and len(self.trail) > 1:
            for i in range(0, len(self.trail)-1, 4):
                pygame.draw.line(surf, (150,150,150), self.trail[i], self.trail[i+1], 2)
        pygame.draw.circle(surf, PROJECTILE_COLOR, (int(self.x), int(self.y)), self.radius)

class Target:
    def __init__(self, x, y, radius=TARGET_RADIUS, mobile=False):
        self.base_x = x
        self.x = x
        self.y = y
        self.radius = radius
        self.mobile = mobile
        self.t = 0.0
        self.amp = random.uniform(50, 150)
        self.speed = random.uniform(0.6, 1.6)

    def update(self, dt):
        if self.mobile:
            self.t += dt
            self.x = self.base_x + math.sin(self.t * self.speed) * self.amp

    def draw(self, surf):
        pygame.draw.circle(surf, TARGET_COLOR, (int(self.x), int(self.y)), self.radius)
        pygame.draw.circle(surf, (255,255,255), (int(self.x), int(self.y)), int(self.radius*0.4))

    def check_hit(self, proj):
        dx = self.x - proj.x
        dy = self.y - proj.y
        return dx*dx + dy*dy <= (self.radius + proj.radius)**2

# Main

def main():
    global ENABLE_WIND, WIND_ACCEL, ENABLE_DRAG, SHOW_TRAIL, MOBILE_TARGET

    pygame.init()
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("Juego del Cañón - Prototipo")
    clock = pygame.time.Clock()
    font = pygame.font.SysFont(None, 24)

    angle_deg = 35
    power = 400.0
    projectile = None
    score = 0
    message = ""
    message_timer = 0.0

    target = Target(650, HEIGHT - 120, mobile=MOBILE_TARGET)

    running = True
    while running:
        dt = clock.tick(FPS) / 1000.0

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE and projectile is None:
                    rad = math.radians(angle_deg)
                    vx = math.cos(rad) * power
                    vy = -math.sin(rad) * power
                    projectile = Projectile((CANNON_POS[0] + CANNON_LENGTH*math.cos(rad), CANNON_POS[1] - CANNON_LENGTH*math.sin(rad)), (vx, vy))
                elif event.key == pygame.K_r:
                    projectile = None
                    target = Target(random.randint(500, WIDTH-80), HEIGHT - 120, mobile=MOBILE_TARGET)
                    message = ""
                elif event.key == pygame.K_m:
                    MOBILE_TARGET = not MOBILE_TARGET
                    target.mobile = MOBILE_TARGET
                elif event.key == pygame.K_w:
                    ENABLE_WIND = not ENABLE_WIND
                    WIND_ACCEL = random.uniform(-200, 200) if ENABLE_WIND else 0.0
                elif event.key == pygame.K_a:
                    ENABLE_DRAG = not ENABLE_DRAG
                elif event.key == pygame.K_t:
                    SHOW_TRAIL = not SHOW_TRAIL

        keys = pygame.key.get_pressed()
        if keys[pygame.K_UP]: angle_deg = clamp(angle_deg + 60*dt, 0, 85)
        if keys[pygame.K_DOWN]: angle_deg = clamp(angle_deg - 60*dt, 0, 85)
        if keys[pygame.K_RIGHT]: power = clamp(power + 200*dt, 50, 1200)
        if keys[pygame.K_LEFT]: power = clamp(power - 200*dt, 50, 1200)

        target.update(dt)
        if projectile:
            wind_ax = WIND_ACCEL if ENABLE_WIND else 0.0
            projectile.update(dt, wind_ax, ENABLE_DRAG)
            if target.check_hit(projectile):
                message = "¡Has acertado!"
                message_timer = 2.0
                score += 1
                projectile.alive = False
            if not projectile.alive:
                projectile = None

        if message_timer > 0:
            message_timer -= dt
            if message_timer <= 0: message = ""

        screen.fill((135,206,235))
        pygame.draw.rect(screen, (85,170,60), (0, HEIGHT-60, WIDTH, 60))

        rad = math.radians(angle_deg)
        barrel_end = (CANNON_POS[0] + CANNON_LENGTH * math.cos(rad), CANNON_POS[1] - CANNON_LENGTH * math.sin(rad))
        pygame.draw.circle(screen, CANNON_COLOR, CANNON_POS, 22)
        pygame.draw.line(screen, CANNON_COLOR, CANNON_POS, barrel_end, 8)

        target.draw(screen)
        if projectile: projectile.draw(screen)

        # HUD y controles
        controls = ["CONTROLES:", "M → Diana móvil ON/OFF", "W → Viento ON/OFF", "A → Rozamiento del aire ON/OFF", "T → Estela ON/OFF"]
        for i, line in enumerate(controls):
            surf = font.render(line, True, (10,10,10))
            screen.blit(surf, (10, 60 + i*20))

        hud_lines = [f"Ángulo: {angle_deg:.1f}°  Potencia: {power:.0f} px/s  Puntuación: {score}",
                     f"Viento: {'ON' if ENABLE_WIND else 'OFF'} ({WIND_ACCEL:.1f})  Rozamiento: {'ON' if ENABLE_DRAG else 'OFF'}  Diana móvil: {'ON' if MOBILE_TARGET else 'OFF'}"]
        for i, line in enumerate(hud_lines):
            surf = font.render(line, True, (10,10,10))
            screen.blit(surf, (10, 10 + i*22))

        if message:
            big = pygame.font.SysFont(None, 48).render(message, True, (255,40,40))
            screen.blit(big, (WIDTH//2 - big.get_width()//2, 40))

        # Predictive dotted line
        predict_points = []
        sim_x = barrel_end[0]
        sim_y = barrel_end[1]
        sim_vx = math.cos(rad) * power
        sim_vy = -math.sin(rad) * power
        sim_dt = 0.03
        for _ in range(60):
            if ENABLE_DRAG:
                sim_vx += (-DRAG_COEFF*sim_vx)*sim_dt
                sim_vy += (GRAVITY - DRAG_COEFF*sim_vy)*sim_dt
            else:
                sim_vx += (WIND_ACCEL if ENABLE_WIND else 0.0)*sim_dt
                sim_vy += GRAVITY*sim_dt
            sim_x += sim_vx*sim_dt
            sim_y += sim_vy*sim_dt
            if sim_y > HEIGHT-60: break
            predict_points.append((int(sim_x), int(sim_y)))
        if len(predict_points) > 1:
            for i in range(0, len(predict_points)-1, 4):
                pygame.draw.line(screen, (0,0,0), predict_points[i], predict_points[i+1], 1)

        pygame.display.flip()

    pygame.quit()

if __name__ == '__main__':
    main()
