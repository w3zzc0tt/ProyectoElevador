import pygame
import sys

pygame.init()

# Tamaño de la pantalla
ANCHO, ALTO = 900, 600
screen = pygame.display.set_mode((ANCHO, ALTO))
pygame.display.set_caption("Panel de Ascensor")

# Colores
GRIS_FONDO = (168, 168, 168)
NEGRO_PANEL = (10, 10, 10)
VERDE_LED = (0, 255, 0)
BLANCO = (255, 255, 255)
GRIS_OSCURO = (40, 40, 40)
ROJO = (255, 50, 50)
GRIS_CLARO = (200, 200, 200)

# Fuente
fuente = pygame.font.SysFont("Courier New", 36, bold=True)
fuente_led = pygame.font.SysFont("Courier New", 48, bold=True)

# Estados de menú
MENU_PRINCIPAL = 0
MENU_DIFICULTAD = 1
MENU_CONFIG = 2
MENU_SALIR = 3

estado_actual = MENU_PRINCIPAL

# Diccionario de opciones por menú
menus = {
    MENU_PRINCIPAL: ["1. Jugar", "2. Configuración", "3. Salir"],
    MENU_DIFICULTAD: ["1. Fácil", "2. Normal", "3. Difícil", "4. Volver"],
    MENU_CONFIG: ["1. Volumen", "2. Activar shake", "3. Volver"],
    MENU_SALIR: ["1. Confirmar salida", "2. Cancelar"]
}

altura_opcion = 60
panel_top = 100
panel_left = 150
panel_width = 300
panel_height = 400

ascensor_width = 20
ascensor_height = 20
ascensor_x = panel_left - 30
ascensor_y = panel_top + 30
ascensor_color = ROJO

opcion_seleccionada = 0
ascensor_target_y = ascensor_y

clock = pygame.time.Clock()

def volver_al_menu_principal():
    global estado_actual, opcion_seleccionada
    estado_actual = MENU_PRINCIPAL
    opcion_seleccionada = 0

def manejar_seleccion():
    global estado_actual, opcion_seleccionada
    if estado_actual == MENU_PRINCIPAL:
        if opcion_seleccionada == 0:
            estado_actual = MENU_DIFICULTAD
        elif opcion_seleccionada == 1:
            estado_actual = MENU_CONFIG
        elif opcion_seleccionada == 2:
            estado_actual = MENU_SALIR
        opcion_seleccionada = 0
    elif estado_actual == MENU_DIFICULTAD:
        if opcion_seleccionada == 3:
            volver_al_menu_principal()
    elif estado_actual == MENU_CONFIG:
        if opcion_seleccionada == 2:
            volver_al_menu_principal()
    elif estado_actual == MENU_SALIR:
        if opcion_seleccionada == 1:
            volver_al_menu_principal()
        elif opcion_seleccionada == 0:
            pygame.quit()
            sys.exit()

def dibujar_interfaz():
    screen.fill(GRIS_FONDO)

    # Marco gris (interior ascensor)
    pygame.draw.rect(screen, GRIS_OSCURO, (panel_left - 20, panel_top - 20, panel_width + 40, panel_height + 40))

    # Panel negro
    pygame.draw.rect(screen, NEGRO_PANEL, (panel_left, panel_top, panel_width, panel_height))

    # Panel digital (encima)
    piso_txt = fuente_led.render(str(opcion_seleccionada + 1), True, VERDE_LED)
    screen.blit(piso_txt, (panel_left + panel_width // 2 - piso_txt.get_width() // 2, panel_top + 10))

    # Opciones actuales
    opciones = menus[estado_actual]
    for i, opcion in enumerate(opciones):
        y = panel_top + 100 + i * altura_opcion
        color = BLANCO if i == opcion_seleccionada else GRIS_CLARO
        texto = fuente.render(opcion, True, color)
        screen.blit(texto, (panel_left + 60, y))

        # LED indicador
        led_color = VERDE_LED if i == opcion_seleccionada else (60, 60, 60)
        pygame.draw.circle(screen, led_color, (panel_left + 30, y + 20), 8)

    # Ascensor miniatura
    pygame.draw.rect(screen, ascensor_color, (ascensor_x, ascensor_y, ascensor_width, ascensor_height))

# Loop principal
while True:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()

        elif event.type == pygame.KEYDOWN:
            if pygame.K_1 <= event.key <= pygame.K_9:
                opcion_presionada = event.key - pygame.K_1
                if 0 <= opcion_presionada < len(menus[estado_actual]):
                    opcion_seleccionada = opcion_presionada
                    manejar_seleccion()

        elif event.type == pygame.MOUSEMOTION:
            mouse_x, mouse_y = event.pos
            opciones = menus[estado_actual]
            for i in range(len(opciones)):
                y = panel_top + 100 + i * altura_opcion
                if panel_left < mouse_x < panel_left + panel_width and y < mouse_y < y + altura_opcion:
                    opcion_seleccionada = i

        elif event.type == pygame.MOUSEBUTTONDOWN:
            manejar_seleccion()

    # Animación del ascensor
    ascensor_target_y = panel_top + 100 + opcion_seleccionada * altura_opcion + 10
    ascensor_y += (ascensor_target_y - ascensor_y) * 0.1

    dibujar_interfaz()
    pygame.display.flip()
    clock.tick(60)
