import pygame
import sys
from logica_ascensor import iniciar_ascensor, actualizar_ascensor, dibujar_pisos

# Inicializar Pygame
pygame.init()
ANCHO, ALTO = 900, 600
screen = pygame.display.set_mode((ANCHO, ALTO))
pygame.display.set_caption("Test Ascensor")
clock = pygame.time.Clock()

# Mock: Persona simple (puede ser string para test)
class PersonaMock:
    def __init__(self, nombre):
        self.nombre = nombre
        self.area_ocupada = 1
        self.imagen = None  # Para compatibilidad con lógica de juego real

# Mock: Elevador con 10 personas
class ElevadorMock:
    def __init__(self):
        self.personas_dentro = [PersonaMock(f"Persona {i+1}") for i in range(10)]
        self.area_ocupada = len(self.personas_dentro)

# Función de retorno al menú (simulada)
def volver_dummy():
    print("Volver al menú (simulado)")

# Contexto para lógica del ascensor
elevador = ElevadorMock()
contexto = {
    'elevador': elevador,
    'volver_al_menu_principal': volver_dummy,
    'COLORES': {
        "fondo": (20, 20, 30),
        "texto_activo": (255, 255, 255),
        "advertencia": (255, 200, 0)
    },
    'fuente_pequena': pygame.font.SysFont("Courier New", 20)
}

# Iniciar la lógica del ascensor
iniciar_ascensor(contexto)

# Bucle principal
running = True
while running:
    screen.fill((30, 30, 40))  # Fondo alternativo si falla el fondo de pisos

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.USEREVENT + 10:
            print("Fin del ascensor, volver al lobby.")
            running = False

    actualizar_ascensor()
    dibujar_pisos(screen)

    pygame.display.flip()
    clock.tick(60)

pygame.quit()
sys.exit()
