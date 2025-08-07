import pygame
from menu_principal import manejar_menu
import lobby
from elevador import Elevador
from temporizadores import TemporizadorGameplay
from reglas_tutorial import mostrar_reglas_tutorial
pygame.init()

ANCHO, ALTO = 900, 600
screen = pygame.display.set_mode((ANCHO, ALTO))
pygame.display.set_caption("Menú Principal")

fuente = pygame.font.SysFont("Courier New", 32, bold=True)
fuente_led = pygame.font.SysFont("Courier New", 48, bold=True)
fuente_pequena = pygame.font.SysFont("Courier New", 22, bold=True)
fuente_mediana = pygame.font.SysFont("Courier New", 28, bold=True)
clock = pygame.time.Clock()

COLORES = {
    "panel_interior": (80, 80, 90),
    "borde_panel": (120, 120, 140),
    "display_fondo": (10, 20, 10),
    "display_borde": (0, 80, 0),
    "verde_led": (0, 255, 100),
    "verde_led_claro": (150, 255, 150),
    "texto_activo": (255, 255, 255),
    "texto_inactivo": (200, 200, 200),
    "opcion_activa": (50, 50, 70),
    "opcion_inactiva": (40, 40, 50),
    "borde_opcion": (100, 100, 120),
    "ascensor": (255, 70, 70),
    "sombra_ascensor": (30, 30, 30),
    "brillo_ascensor": (200, 200, 200),
    "advertencia": (255, 100, 100),
    "exito": (50, 255, 50),
    "error": (255, 50, 50)
}

panel_surface_oscura = pygame.Surface((ANCHO, ALTO), pygame.SRCALPHA)
panel_surface_oscura.fill((0, 0, 0, 140))

def mostrar_mensaje_temporal(texto, tipo):
    print(f"[{tipo.upper()}] {texto}")

# Bandera global para controlar el ciclo principal
salir_del_juego = False

def volver_al_menu_principal():
    global salir_del_juego
    # Simplemente retorna el control al ciclo principal
    pass

# Bucle principal del juego
while not salir_del_juego:
    accion = manejar_menu(screen, COLORES, fuente, fuente_led, panel_surface_oscura, ANCHO, ALTO, clock)

    if accion in ["FACIL", "NORMAL", "DIFICIL"]:
        lobby.reiniciar_juego()
        
        elevador = Elevador()
        fondo_lobby = pygame.image.load("assets/lobby.png").convert()
        fondo_lobby = pygame.transform.scale(fondo_lobby, (ANCHO, ALTO))
        fondo_pos_x_lobby = 0
        fondo_pos_y_lobby = 0

        temporizador_gameplay = TemporizadorGameplay()

        contexto = {
            "screen": screen,
            "ANCHO": ANCHO,
            "ALTO": ALTO,
            "COLORES": COLORES,
            "fuente": fuente,
            "fuente_pequena": fuente_pequena,
            "fuente_mediana": fuente_mediana,
            "fuente_led": fuente_led,
            "clock": clock,
            "panel_surface_oscura": panel_surface_oscura,
            "dificultad_actual": accion,
            "temporizador_gameplay": temporizador_gameplay,
            "elevador": elevador,
            "fondo_lobby": fondo_lobby,
            "fondo_pos_x_lobby": 0,
            "fondo_pos_y_lobby": 0,
            "Dificultad": accion,
            "mostrar_mensaje_temporal": mostrar_mensaje_temporal,
            "volver_al_menu_principal": volver_al_menu_principal
        }

        lobby.iniciar_lobby(contexto)
        lobby.bucle_lobby()
    elif accion == "config":
        # Simple configuration menu implementation
        volumen_activo = True
        
        # Simple configuration loop
        config_running = True
        while config_running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    salir_del_juego = True
                    config_running = False
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        config_running = False
                    elif event.key == pygame.K_RETURN:
                        # Toggle volumen
                        volumen_activo = not volumen_activo
                        if volumen_activo:
                            pygame.mixer.music.set_volume(1.0)
                            print("Volumen activado")
                        else:
                            pygame.mixer.music.set_volume(0.0)
                            print("Volumen desactivado")
                    elif event.key == pygame.K_BACKSPACE:
                        config_running = False
            
            # Simple display
            screen.fill((30, 30, 40))
            title = fuente.render("CONFIGURACION", True, (0, 255, 100))
            screen.blit(title, (ANCHO//2 - title.get_width()//2, 100))
            
            estado = fuente.render(f"Volumen: {'ACTIVADO' if volumen_activo else 'DESACTIVADO'}", True, (255, 255, 255))
            screen.blit(estado, (ANCHO//2 - estado.get_width()//2, 250))
            
            instructions = fuente.render("ENTER: Cambiar volumen | ESC: Volver", True, (200, 200, 200))
            screen.blit(instructions, (ANCHO//2 - instructions.get_width()//2, 350))
            
            pygame.display.flip()
            clock.tick(60)
    elif accion == "reglas":
        resultado = mostrar_reglas_tutorial(screen, COLORES, fuente, fuente_pequena, fuente_mediana, ANCHO, ALTO, clock)
        if resultado == "salir":
            salir_del_juego = True
    elif accion == "salir":
        salir_del_juego = True
