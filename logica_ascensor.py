import pygame
import time
import random

# Configuración
tamano_pantalla = (900, 600)
screen_ancho, screen_alto = tamano_pantalla
pisos_totales = 4  # Pisos 1 a 4, lobby es piso 0

# Estado del ascensor
personas_en_ascensor = []
piso_actual = 0
subiendo = False
bajando = False
esperando_en_piso = False
tiempo_ultimo_piso = 0
sprite_cargado = False
tiempo_espera_piso = 1000  # ms
evento_enviado = False  # 🔧 Previene múltiples eventos USEREVENT+10

# Recursos
fondo_pisos = None
ascensor_img = None
ascensor_tamano = (96, 94)
ascensor_pos = [400, 480]

# Contexto desde main
elevador = None
volver_al_menu_principal = None
COLORES = None
fuente_pequena = None

# Posiciones manuales de cada piso (incluye lobby)
pisos_posiciones = [
    (385, 485),  # Lobby (0)
    (385, 315),  # Piso 1
    (385, 270),  # Piso 2
    (385, 150),  # Piso 3
    (385, 90),   # Piso 4
]

# Personas saliendo visualmente
personas_saliendo = []  # Lista de diccionarios con {'sprite', 'x', 'y', 'direccion', 'velocidad'}

def importar_desde_main(modulo_main):
    global elevador, volver_al_menu_principal, COLORES, fuente_pequena
    elevador = getattr(modulo_main, 'elevador', None)
    volver_al_menu_principal = getattr(modulo_main, 'volver_al_menu_principal', None)
    COLORES = getattr(modulo_main, 'COLORES', None)
    fuente_pequena = getattr(modulo_main, 'fuente_pequena', None)

def iniciar_ascensor(contexto):
    global elevador, volver_al_menu_principal, COLORES, fuente_pequena
    global personas_en_ascensor, piso_actual, subiendo, bajando
    global esperando_en_piso, tiempo_ultimo_piso, sprite_cargado, personas_saliendo, evento_enviado

    elevador = contexto['elevador']
    volver_al_menu_principal = contexto['volver_al_menu_principal']
    COLORES = contexto['COLORES']
    fuente_pequena = contexto['fuente_pequena']

    personas_en_ascensor = elevador.personas_dentro.copy()
    elevador.personas_dentro.clear()
    elevador.area_ocupada = 0

    piso_actual = 0
    subiendo = True
    bajando = False
    esperando_en_piso = False
    personas_saliendo.clear()
    tiempo_ultimo_piso = pygame.time.get_ticks()
    cargar_sprites()
    sprite_cargado = True
    evento_enviado = False  # ✅ Reiniciar para que funcione correctamente cada vez
    
def cargar_sprites():
    global fondo_pisos, ascensor_img
    try:
        fondo_pisos = pygame.image.load("assets/pisos.png").convert()
        fondo_pisos = pygame.transform.scale(fondo_pisos, tamano_pantalla)
    except Exception as e:
        print("Error cargando fondo de pisos:", e)

    try:
        ascensor_img = pygame.image.load("assets/ascensor.png").convert_alpha()
        ascensor_img = pygame.transform.scale(ascensor_img, ascensor_tamano)
    except Exception as e:
        print("Error cargando sprite del ascensor:", e)

def actualizar_ascensor():
    global piso_actual, tiempo_ultimo_piso, esperando_en_piso
    global personas_en_ascensor, subiendo, bajando, personas_saliendo
    global evento_enviado  # 👈 asegúrate de tener esta variable global iniciada como False

    ahora = pygame.time.get_ticks()

    if subiendo:
        if esperando_en_piso:
            if ahora - tiempo_ultimo_piso >= tiempo_espera_piso:
                esperando_en_piso = False
                tiempo_ultimo_piso = ahora
                piso_actual += 1
        else:
            if ahora - tiempo_ultimo_piso >= 1500:
                if piso_actual < pisos_totales:
                    if piso_actual > 0:
                        cantidad = random.randint(1, 3)
                        personas_a_bajar = []
                        for _ in range(min(cantidad, len(personas_en_ascensor))):
                            persona = personas_en_ascensor.pop(0)
                            persona.cargar_imagen()
                            personas_a_bajar.append(persona)

                        direccion = "izquierda" if piso_actual in [1, 3] else "derecha"
                        x_inicio, y_inicio = pisos_posiciones[piso_actual]
                        for idx, persona in enumerate(personas_a_bajar):
                            offset_x = idx * 70 if direccion == "derecha" else -idx * 70
                            personas_saliendo.append({
                                "sprite": persona.imagen,
                                "x": x_inicio + 10 + offset_x,
                                "y": y_inicio + 20,
                                "direccion": direccion,
                                "velocidad": 2
                            })
                    esperando_en_piso = True
                    tiempo_ultimo_piso = ahora
                else:
                    personas_en_ascensor.clear()
                    subiendo = False
                    bajando = True
                    tiempo_ultimo_piso = ahora

    elif bajando:
        if ahora - tiempo_ultimo_piso >= 1500:
            if piso_actual > 0:
                piso_actual -= 1
                tiempo_ultimo_piso = ahora
            else:
                bajando = False
                if not evento_enviado:
                    pygame.event.post(pygame.event.Event(pygame.USEREVENT + 10))
                    evento_enviado = True  # 👈 para que no se dispare múltiples veces


def volver_al_lobby():
    pygame.time.set_timer(pygame.USEREVENT + 10, 1000)

def dibujar_pisos(screen):
    print("🏗️ DIBUJANDO ASCENSOR")
    if not sprite_cargado:
        cargar_sprites()
        # No returns aquí: seguimos para dibujar

    screen.fill((0, 0, 0))  # <-- ESTA LÍNEA ES LA CLAVE

    if fondo_pisos:
        screen.blit(fondo_pisos, (0, 0))

    if piso_actual < len(pisos_posiciones):
        x_ascensor, y_ascensor = pisos_posiciones[piso_actual]
    else:
        x_ascensor, y_ascensor = ascensor_pos

    if ascensor_img:
        screen.blit(ascensor_img, (x_ascensor, y_ascensor))

    fuente = pygame.font.SysFont("Courier New", 24, bold=True)
    piso_txt = fuente.render(f"Piso {piso_actual}", True, (255, 255, 255))
    personas_txt = fuente.render(f"Personas restantes: {len(personas_en_ascensor)}", True, (255, 255, 255))
    screen.blit(piso_txt, (20, 20))
    screen.blit(personas_txt, (20, 50))

    # Dibujar personas saliendo visualmente
    for persona in personas_saliendo[:]:
        if persona["sprite"]:
            screen.blit(persona["sprite"], (persona["x"], persona["y"]))
            if persona["direccion"] == "izquierda":
                persona["x"] -= persona["velocidad"]
                if persona["x"] <= 0:
                    personas_saliendo.remove(persona)
            else:
                persona["x"] += persona["velocidad"]
                if persona["x"] + 60 >= screen.get_width():
                    personas_saliendo.remove(persona)


