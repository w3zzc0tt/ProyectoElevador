import pygame
import random
import math
import time
import logica_ascensor
from jugadores import PersonaDiscapacitada, PersonaObesa, PersonaTrabajador, PersonaCliente

# Variables globales para el lobby
screen = None
ANCHO = 0
ALTO = 0
COLORES = {}
fuente_pequena = None
fuente_mediana = None
elevador = None
fondo_lobby = None
fondo_pos_x_lobby = 0
fondo_pos_y_lobby = 0
volver_al_menu_principal = None
estado_juego = {"modo": "lobby"}

# Variables de estado
personas_lobby = []
posiciones_personas_lobby = []
persona_seleccionada_lobby = 0
mensaje_temporal = ""
tiempo_mensaje = 0

# 🎯 ZONA EDITABLE DE PERSPECTIVA
Y_PISO_MIN = 450
Y_PISO_MAX = 500
SEPARACION_MINIMA = 35

def iniciar_lobby(contexto):
    global screen, ANCHO, ALTO, COLORES, fuente_pequena, fuente_mediana, elevador
    global fondo_lobby, fondo_pos_x_lobby, fondo_pos_y_lobby
    global volver_al_menu_principal

    screen = contexto['screen']
    ANCHO = contexto['ANCHO']
    ALTO = contexto['ALTO']
    COLORES = contexto['COLORES']
    fuente_pequena = contexto['fuente_pequena']
    fuente_mediana = contexto['fuente_mediana']
    elevador = contexto['elevador']
    fondo_lobby = pygame.transform.scale(
        pygame.image.load("assets/lobby.png").convert(),
        (ANCHO, ALTO)
    )
    fondo_pos_x_lobby = contexto.get('fondo_pos_x_lobby', 0)
    fondo_pos_y_lobby = contexto.get('fondo_pos_y_lobby', 0)
    volver_al_menu_principal = contexto['volver_al_menu_principal']

    global personas_lobby, posiciones_personas_lobby, persona_seleccionada_lobby
    personas_lobby = generar_personas_lobby()
    posiciones_personas_lobby = distribuir_personas_lobby(personas_lobby)
    persona_seleccionada_lobby = 0

def generar_personas_lobby():
    total = 20
    max_obesos = 3
    personas = []
    obesos = 0

    while len(personas) < total:
        p = random.choice([PersonaDiscapacitada, PersonaObesa, PersonaTrabajador, PersonaCliente])()
        if isinstance(p, PersonaObesa) and obesos >= max_obesos:
            continue
        if isinstance(p, PersonaObesa):
            obesos += 1
        p.cargar_imagen()
        personas.append(p)

    return personas

def distribuir_personas_lobby(personas):
    posiciones = []
    ancho, alto = 50, 50
    separacion = SEPARACION_MINIMA

    y_min = Y_PISO_MIN
    y_max = Y_PISO_MAX
    x_min = 50
    x_max = ANCHO - 110

    for _ in personas:
        for _ in range(200):
            y = random.randint(y_min, y_max)
            x = random.randint(x_min, x_max)
            nuevo_centro = (x + ancho // 2, y + alto // 2)

            if all(math.hypot(nuevo_centro[0] - (px + ancho // 2), nuevo_centro[1] - (py + alto // 2)) >= separacion
                   for px, py in posiciones):
                posiciones.append((x, y))
                break
        else:
            posiciones.append((x, y))
    return posiciones

def iniciar_animacion_ascensor():
    logica_ascensor.iniciar_ascensor({
        "elevador": elevador,
        "volver_al_menu_principal": volver_al_menu_principal,
        "COLORES": COLORES,
        "fuente_pequena": fuente_pequena,
        "PersonaDiscapacitada": PersonaDiscapacitada,
        "PersonaObesa": PersonaObesa,
        "PersonaTrabajador": PersonaTrabajador,
        "PersonaCliente": PersonaCliente
    })
    estado_juego["modo"] = "ascensor"
    print("🎬 CAMBIO A MODO ASCENSOR")

def bucle_lobby():
    global mensaje_temporal, tiempo_mensaje

    ejecutando = True
    clock = pygame.time.Clock()

    while ejecutando:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                ejecutando = False

            if estado_juego["modo"] == "lobby":
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        volver_al_menu_principal()
                        ejecutando = False
                    elif event.key == pygame.K_RETURN:
                        seleccionar()
                    elif event.key == pygame.K_RIGHT:
                        mover_seleccion(1)
                    elif event.key == pygame.K_LEFT:
                        mover_seleccion(-1)
                    elif event.key == pygame.K_SPACE:
                        iniciar_animacion_ascensor()

            elif estado_juego["modo"] == "ascensor":
                if event.type == pygame.USEREVENT + 10:
                    print("✅ USEREVENT + 10 recibido")
                    estado_juego["modo"] = "lobby"

        if estado_juego["modo"] == "lobby":
            screen.fill((0, 0, 0))
            dibujar_lobby()
        elif estado_juego["modo"] == "ascensor":
            screen.fill((0, 0, 0))
            logica_ascensor.actualizar_ascensor()
            logica_ascensor.dibujar_pisos(screen)

        pygame.display.flip()
        clock.tick(60)

def dibujar_lobby():
    if fondo_lobby:
        screen.blit(fondo_lobby, (fondo_pos_x_lobby, fondo_pos_y_lobby))

    for i, (x, y) in enumerate(posiciones_personas_lobby):
        if i < len(personas_lobby):
            persona = personas_lobby[i]
            if i == persona_seleccionada_lobby:
                pygame.draw.rect(screen, COLORES["verde_led"], (x - 5, y - 5, 70, 70), 3, border_radius=10)
            if hasattr(persona, 'imagen') and persona.imagen:
                screen.blit(persona.imagen, (x, y))

    mostrar_contadores_lobby()

    instrucciones = "Flechas ← →  : Mover | ENTER: Subir | ESC: Menu"
    txt = fuente_pequena.render(instrucciones, True, COLORES['texto_activo'])
    screen.blit(txt, (ANCHO // 2 - txt.get_width() // 2, ALTO - 40))

    if mensaje_temporal and time.time() < tiempo_mensaje:
        amarillo = (255, 255, 0)
        negro = (0, 0, 0)
        txt = fuente_mediana.render(mensaje_temporal, True, amarillo)
        x = ANCHO // 2 - txt.get_width() // 2
        y = 60

        for dx in [-2, 2]:
            for dy in [-2, 2]:
                sombra = fuente_mediana.render(mensaje_temporal, True, negro)
                screen.blit(sombra, (x + dx, y + dy))

        screen.blit(txt, (x, y))

def mover_seleccion(delta):
    global persona_seleccionada_lobby
    persona_seleccionada_lobby = max(0, min(len(personas_lobby) - 1, persona_seleccionada_lobby + delta))

def seleccionar():
    global personas_lobby, posiciones_personas_lobby, persona_seleccionada_lobby
    if not personas_lobby:
        return
    persona = personas_lobby[persona_seleccionada_lobby]
    if elevador.puede_entrar(persona):
        elevador.entrar_persona(persona)
        personas_lobby.pop(persona_seleccionada_lobby)
        posiciones_personas_lobby.pop(persona_seleccionada_lobby)
        if persona_seleccionada_lobby >= len(personas_lobby):
            persona_seleccionada_lobby = max(0, len(personas_lobby) - 1)
        mostrar_mensaje_en_pantalla(f"{persona.nombre} subió al elevador")
    else:
        mostrar_mensaje_en_pantalla("Sin espacio suficiente en el elevador")

def mostrar_contadores_lobby():
    total = len(personas_lobby)
    trabajadores = sum(isinstance(p, PersonaTrabajador) for p in personas_lobby)
    clientes = sum(isinstance(p, PersonaCliente) for p in personas_lobby)
    disc = sum(isinstance(p, PersonaDiscapacitada) for p in personas_lobby)
    obesos = sum(isinstance(p, PersonaObesa) for p in personas_lobby)

    y = 10
    for txt in [
        f"Personas Restantes: {total}",
        f"Trabajadores: {trabajadores}",
        f"Clientes: {clientes}",
        f"Discapacitados: {disc}",
        f"Obesos: {obesos}",
    ]:
        s = fuente_pequena.render(txt, True, COLORES["texto_activo"])
        screen.blit(s, (10, y))
        y += 30

    elevador_txt = f"Elevador: {elevador.area_ocupada}/9"
    e_s = fuente_pequena.render(elevador_txt, True, COLORES["texto_activo"])
    screen.blit(e_s, (ANCHO - e_s.get_width() - 10, 10))

def mostrar_mensaje_en_pantalla(texto, duracion=2):
    global mensaje_temporal, tiempo_mensaje
    mensaje_temporal = texto
    tiempo_mensaje = time.time() + duracion
