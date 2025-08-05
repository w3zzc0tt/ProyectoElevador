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
penalizacion_pendiente = None

# Variables de estado
personas_lobby = []
posiciones_personas_lobby = []
persona_seleccionada_lobby = 0
cola_mensajes = []  # Nueva cola para almacenar mensajes pendientes
mensaje_actual = ""  # Mensaje que se está mostrando actualmente
tiempo_fin_mensaje = 0  # Tiempo en que termina el mensaje actual
tiempo_espera_entre_mensajes = 0.5  # Tiempo mínimo entre mensajes (en segundos)
puntos = 0  # Variable para el sistema de puntaje

# Sistema de mala reputación dinámica
mala_reputacion = 0  # Contador de trabajadores que se han ido
total_trabajadores = 0  # Total de trabajadores generados al inicio
limite_mala_reputacion = 5  # Límite dinámico antes del Game Over
game_over = False  # Indica si el juego ha terminado
game_over_img = None  # Imagen de Game Over
temporizador_gameplay = None

# 🎯 ZONA EDITABLE DE PERSPECTIVA
Y_PISO_MIN = 450
Y_PISO_MAX = 500
SEPARACION_MINIMA = 35
def reiniciar_juego():
    """Reinicia todas las variables del juego"""
    global puntos, mala_reputacion, total_trabajadores, limite_mala_reputacion
    global personas_lobby, posiciones_personas_lobby, persona_seleccionada_lobby
    global cola_mensajes, mensaje_actual, tiempo_fin_mensaje, tiempo_espera_entre_mensajes
    global game_over, elevador
    
    # Reiniciar variables de puntaje y reputación
    puntos = 0
    mala_reputacion = 0
    total_trabajadores = 0
    limite_mala_reputacion = 5
    game_over = False
    
    # Limpiar listas de personas
    personas_lobby = []
    posiciones_personas_lobby = []
    
    # Reiniciar selección
    persona_seleccionada_lobby = 0
    
    # Limpiar mensajes
    cola_mensajes = []
    mensaje_actual = ""
    tiempo_fin_mensaje = 0
    tiempo_espera_entre_mensajes = 0.5
    
    # Reiniciar el elevador
    try:
        from elevador import Elevador
        elevador = Elevador(9)
    except:
        pass
    
    print("🔄 Juego reiniciado completamente")

def reiniciar_puntaje():
    """Reinicia el puntaje al iniciar un nuevo juego"""
    global puntos, mala_reputacion, total_trabajadores, limite_mala_reputacion, game_over
    puntos = 0
    mala_reputacion = 0
    total_trabajadores = 0
    limite_mala_reputacion = 5
    game_over = False

def iniciar_lobby(contexto):
    global screen, ANCHO, ALTO, COLORES, fuente_pequena, fuente_mediana, elevador
    global fondo_lobby, fondo_pos_x_lobby, fondo_pos_y_lobby
    global volver_al_menu_principal, temporizador_gameplay
    global game_over, game_over_img, mala_reputacion, total_trabajadores, limite_mala_reputacion
    
    # === REINICIO COMPLETO DEL JUEGO ===
    reiniciar_juego()
    
    # Continuar con la inicialización normal
    screen = contexto['screen']
    ANCHO = contexto['ANCHO']
    ALTO = contexto['ALTO']
    COLORES = contexto['COLORES']
    fuente_pequena = contexto['fuente_pequena']
    fuente_mediana = contexto['fuente_mediana']
    elevador = contexto['elevador']
    
    # Cargar imagen de Game Over
    try:
        game_over_img = pygame.image.load("assets/gameover.png").convert()
        game_over_img = pygame.transform.scale(game_over_img, (ANCHO, ALTO))
    except Exception as e:
        print(f"Error al cargar la imagen de Game Over: {e}")
        # Crear una imagen de Game Over simple si no se puede cargar la imagen
        game_over_img = pygame.Surface((ANCHO, ALTO))
        game_over_img.fill((0, 0, 0))
        font = pygame.font.SysFont(None, 72)
        text = font.render("GAME OVER", True, (255, 0, 0))
        game_over_img.blit(text, (ANCHO//2 - text.get_width()//2, ALTO//2 - text.get_height()//2))
    
    fondo_lobby = pygame.transform.scale(
        pygame.image.load("assets/lobby.png").convert(),
        (ANCHO, ALTO)
    )
    fondo_pos_x_lobby = contexto.get('fondo_pos_x_lobby', 0)
    fondo_pos_y_lobby = contexto.get('fondo_pos_y_lobby', 0)
    volver_al_menu_principal = contexto['volver_al_menu_principal']
    temporizador_gameplay = contexto.get('temporizador_gameplay')
    if temporizador_gameplay:
        temporizador_gameplay.iniciar()

    global personas_lobby, posiciones_personas_lobby, persona_seleccionada_lobby
    personas_lobby = generar_personas_lobby()
    posiciones_personas_lobby = distribuir_personas_lobby(personas_lobby)
    persona_seleccionada_lobby = 0

def generar_personas_lobby():
    total = 20
    max_obesos = 3
    personas = []
    obesos = 0
    global total_trabajadores
    
    while len(personas) < total:
        p = random.choice([PersonaDiscapacitada, PersonaObesa, PersonaTrabajador, PersonaCliente])()
        if isinstance(p, PersonaObesa) and obesos >= max_obesos:
            continue
        if isinstance(p, PersonaObesa):
            obesos += 1
        p.cargar_imagen()
        # Iniciar temporizador si es trabajador
        if isinstance(p, PersonaTrabajador):
            p.iniciar_temporizador()
            total_trabajadores += 1
        personas.append(p)
    
    # Calcular el límite de mala reputación (65% del total de trabajadores)
    global limite_mala_reputacion
    limite_mala_reputacion = max(1, int(total_trabajadores * 0.65))
    
    print(f"Total de trabajadores: {total_trabajadores}")
    print(f"Límite de mala reputación (65%): {limite_mala_reputacion}")
    
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
    # Verificar si el elevador tiene personas (si hay una ronda en curso)
    if elevador.personas_dentro:
        # Verificar si hay AL MENOS UN discapacitado en el elevador
        hay_discapacitado = False
        for persona in elevador.personas_dentro:
            # Verificar de múltiples maneras para asegurar compatibilidad
            if hasattr(persona, 'tipo') and persona.tipo == "Discapacitado":
                hay_discapacitado = True
                break
            elif isinstance(persona, PersonaDiscapacitada):
                hay_discapacitado = True
                break
        
        # Aplicar penalización SOLO si NO hay ningún discapacitado en el elevador
        if not hay_discapacitado:
            global puntos
            puntos -= 5
            mostrar_mensaje_en_pantalla("¡PENALIZACIÓN! -5 puntos por no subir un discapacitado", 3)
            print("⚠️ PENALIZACIÓN: No había discapacitados en el elevador (-5 puntos)")
    
    # Continuar con la animación del ascensor
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
    global mensaje_temporal, tiempo_mensaje, game_over
    
    ejecutando = True
    clock = pygame.time.Clock()

    while ejecutando:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                ejecutando = False

            if estado_juego["modo"] == "lobby" and not game_over:
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
        
        # Manejar Game Over
        if game_over:
            screen.blit(game_over_img, (0, 0))
            pygame.display.flip()
            pygame.time.wait(3000)  # Mostrar la pantalla de Game Over por 3 segundos
            volver_al_menu_principal()
            ejecutando = False
            return

        # Actualizar estado del lobby (incluyendo trabajadores enojados)
        if estado_juego["modo"] == "lobby" and not game_over:
            actualizar_estado_lobby()
            
            # Verificar temporizador de gameplay
            if temporizador_gameplay:
                terminado = temporizador_gameplay.actualizar()
                if terminado:
                    mostrar_mensaje_en_pantalla("¡Tiempo agotado! Fin del juego.", 5)
                    pygame.time.wait(2000)
                    volver_al_menu_principal()
                    ejecutando = False
            
            screen.fill((0, 0, 0))
            dibujar_lobby()
        elif estado_juego["modo"] == "ascensor" and not game_over:
            screen.fill((0, 0, 0))
            logica_ascensor.actualizar_ascensor()
            logica_ascensor.dibujar_pisos(screen)

        pygame.display.flip()
        clock.tick(60)

def dibujar_lobby():
    global cola_mensajes, mensaje_actual, tiempo_fin_mensaje, tiempo_espera_entre_mensajes
    
    if fondo_lobby:
        screen.blit(fondo_lobby, (fondo_pos_x_lobby, fondo_pos_y_lobby))
    if temporizador_gameplay:
        temporizador_gameplay.dibujar_temporizador_principal(
            screen, fuente_mediana, COLORES, ANCHO
            )
        
    for i, (x, y) in enumerate(posiciones_personas_lobby):
        if i < len(personas_lobby):
            persona = personas_lobby[i]
            if hasattr(persona, "temporizador"):
                persona.temporizador.dibujar_barra(
                    screen, x, y + 62, 60, 6, COLORES)
                persona.temporizador.actualizar()
        
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
    
    # Mostrar advertencia de mala reputación crítica
    if mala_reputacion >= limite_mala_reputacion - 2 and mala_reputacion < limite_mala_reputacion:
        advertencia = "¡CUIDADO! Los trabajadores están perdiendo la paciencia"
        amarillo = (255, 255, 0)
        negro = (0, 0, 0)
        txt = fuente_pequena.render(advertencia, True, amarillo)
        x = ANCHO // 2 - txt.get_width() // 2
        y = ALTO - 70

        for dx in [-2, 2]:
            for dy in [-2, 2]:
                sombra = fuente_pequena.render(advertencia, True, negro)
                screen.blit(sombra, (x + dx, y + dy))

        screen.blit(txt, (x, y))

    # Mostrar mensaje temporal (manejo de cola)
    # Si hay mensajes en la cola y ha pasado suficiente tiempo desde el último mensaje
    if cola_mensajes and (time.time() > tiempo_fin_mensaje + tiempo_espera_entre_mensajes):
        texto, duracion = cola_mensajes.pop(0)
        mensaje_actual = texto
        tiempo_fin_mensaje = time.time() + duracion
        print(f"[MENSAJE] Mostrando mensaje: '{texto}'")

    # Mostrar el mensaje actual si existe y aún no ha expirado
    if mensaje_actual and time.time() < tiempo_fin_mensaje:
        amarillo = (255, 255, 0)
        negro = (0, 0, 0)
        txt = fuente_mediana.render(mensaje_actual, True, amarillo)
        x = ANCHO // 2 - txt.get_width() // 2
        y = 60

        for dx in [-2, 2]:
            for dy in [-2, 2]:
                sombra = fuente_mediana.render(mensaje_actual, True, negro)
                screen.blit(sombra, (x + dx, y + dy))

        screen.blit(txt, (x, y))

def mover_seleccion(delta):
    global persona_seleccionada_lobby
    persona_seleccionada_lobby = max(0, min(len(personas_lobby) - 1, persona_seleccionada_lobby + delta))

def seleccionar():
    global personas_lobby, posiciones_personas_lobby, persona_seleccionada_lobby, puntos
    
    if not personas_lobby:
        return
        
    # Asegurar que el índice de selección esté dentro del rango válido
    if persona_seleccionada_lobby >= len(personas_lobby):
        persona_seleccionada_lobby = max(0, len(personas_lobby) - 1)
        if not personas_lobby:  # Si no hay personas después del ajuste
            return
            
    persona = personas_lobby[persona_seleccionada_lobby]
    
    # Verificar si puede entrar al elevador
    if elevador.puede_entrar(persona):
        # Agregar persona al elevador
        elevador.entrar_persona(persona)
        # Remover la persona seleccionada del lobby
        personas_lobby.pop(persona_seleccionada_lobby)
        posiciones_personas_lobby.pop(persona_seleccionada_lobby)
        # Ajustar índice de selección
        if personas_lobby:
            persona_seleccionada_lobby = min(persona_seleccionada_lobby, len(personas_lobby) - 1)
        else:
            persona_seleccionada_lobby = 0
        # Calcular puntos según el tipo de persona
        mensaje = f"{getattr(persona, 'nombre', 'Persona')} subió al elevador"
        if isinstance(persona, PersonaCliente):
            puntos += 1
            mensaje += " (+1)"
        elif isinstance(persona, PersonaTrabajador):
            puntos += 2
            mensaje += " (+2)"
        elif isinstance(persona, PersonaObesa):
            puntos += 3
            mensaje += " (+3)"
        elif isinstance(persona, PersonaDiscapacitada):
            puntos += 4
            mensaje += " (+4)"
        else:
            puntos += 1
            mensaje += " (+1)"
        if puntos > 100:
            puntos = 100
        mensaje += f" | Puntaje: {puntos}"
        mostrar_mensaje_en_pantalla(mensaje, 3)
    else:
        if elevador.area_ocupada >= elevador.capacidad_area:
            mostrar_mensaje_en_pantalla("Elevador lleno, presiona ESPACIO para continuar", 3)
        else:
            mostrar_mensaje_en_pantalla("Sin espacio suficiente en el elevador", 2)

def actualizar_estado_lobby():
    """Actualiza el estado del lobby, incluyendo la verificación de trabajadores enojados"""
    global personas_lobby, posiciones_personas_lobby, persona_seleccionada_lobby, puntos, mala_reputacion, game_over
    
    # Lista para almacenar los índices de trabajadores a eliminar
    trabajadores_a_eliminar = []
    
    # Verificar cada persona en el lobby
    for i, persona in enumerate(personas_lobby):
        # Verificar si es un trabajador con temporizador
        if isinstance(persona, PersonaTrabajador) and hasattr(persona, 'temporizador') and persona.temporizador:
            # Actualizar el temporizador y verificar si terminó
            if persona.temporizador.actualizar():
                trabajadores_a_eliminar.append(i)
    
    # Eliminar trabajadores y aplicar penalizaciones
    for i in reversed(trabajadores_a_eliminar):
        if i < len(personas_lobby):
            persona = personas_lobby[i]
            # Aplicar penalización
            puntos -= 4
            mostrar_mensaje_en_pantalla(f"{persona.nombre} se fue molesto (-4)", 3)
            
            # Incrementar mala reputación
            mala_reputacion += 1
            
            # Eliminar de las listas
            personas_lobby.pop(i)
            posiciones_personas_lobby.pop(i)
            
            # Ajustar índice de selección si es necesario
            if persona_seleccionada_lobby > i:
                persona_seleccionada_lobby -= 1
            elif persona_seleccionada_lobby == i and persona_seleccionada_lobby >= len(personas_lobby):
                persona_seleccionada_lobby = max(0, len(personas_lobby) - 1)
    
    # Verificar si se alcanzó el límite de mala reputación
    if mala_reputacion >= limite_mala_reputacion:
        game_over = True

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
        f"Complexión Robusta: {obesos}",
    ]:
        s = fuente_pequena.render(txt, True, COLORES["texto_activo"])
        screen.blit(s, (10, y))
        y += 30
    
    # Mostrar el puntaje
    color_puntaje = COLORES["exito"] if puntos >= 0 else COLORES["error"]
    puntaje_txt = f"PUNTAJE: {puntos}"
    s = fuente_pequena.render(puntaje_txt, True, color_puntaje)
    screen.blit(s, (10, y))
    y += 30
    
    # Mostrar la mala reputación dinámica
    porcentaje = (mala_reputacion / limite_mala_reputacion) * 100
    if porcentaje >= 80:
        color_reputacion = COLORES["error"]
    elif porcentaje >= 50:
        color_reputacion = COLORES["advertencia"]
    else:
        color_reputacion = COLORES["texto_activo"]
    
    reputacion_txt = f"REPUTACIÓN: {mala_reputacion}/{limite_mala_reputacion}"
    s = fuente_pequena.render(reputacion_txt, True, color_reputacion)
    screen.blit(s, (10, y))
    y += 30

    elevador_txt = f"Elevador: {elevador.area_ocupada}/9"
    e_s = fuente_pequena.render(elevador_txt, True, COLORES["texto_activo"])
    screen.blit(e_s, (ANCHO - e_s.get_width() - 10, 10))

def mostrar_mensaje_en_pantalla(texto, duracion=2):
    """Agrega un mensaje a la cola de mensajes pendientes"""
    global cola_mensajes
    cola_mensajes.append((texto, duracion))
    print(f"[MENSAJE] Mensaje agregado a la cola: '{texto}' (dura {duracion}s)")