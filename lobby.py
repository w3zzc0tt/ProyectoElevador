import pygame
import random
import math
import time
import logica_ascensor
from jugadores import PersonaDiscapacitada, PersonaObesa, PersonaTrabajador, PersonaCliente
from elevador import Elevador
import webbrowser

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
total_discapacitados = 0
penalizaciones_discapacitados = 0
denuncias = 0
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

# Variables para el sistema de éxito
total_personas_inicial = 0  # Total de personas al inicio del juego
tiempo_inicio_juego = 0    # Tiempo cuando inicia el juego

# 🎯 ZONA EDITABLE DE PERSPECTIVA
Y_PISO_MIN = 450
Y_PISO_MAX = 500
SEPARACION_MINIMA = 35

def reiniciar_juego():
    """Reinicia completamente todas las variables del juego"""
    global puntos, mala_reputacion, total_trabajadores, limite_mala_reputacion
    global personas_lobby, posiciones_personas_lobby, persona_seleccionada_lobby
    global cola_mensajes, mensaje_actual, tiempo_fin_mensaje, tiempo_espera_entre_mensajes
    global game_over, elevador
    global total_discapacitados_generados, penalizaciones_discapacitados, denuncias
    
    # Reiniciar variables de puntaje y reputación
    puntos = 0
    mala_reputacion = 0
    total_trabajadores = 0
    limite_mala_reputacion = 5
    game_over = False
    
    # Reiniciar contadores para el sistema de denuncias
    total_discapacitados_generados = 0
    penalizaciones_discapacitados = 0
    denuncias = 0
    
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
    elevador = Elevador(9)
    
    print("🔄 Juego reiniciado completamente")

def contar_discapacitados_inicial():
    global total_discapacitados
    total_discapacitados = sum(isinstance(p, PersonaDiscapacitada) for p in personas_lobby)

def penalizar_discapacitado():
    global penalizaciones_discapacitados, puntos
    penalizaciones_discapacitados += 1
    puntos -= 4
    mostrar_mensaje_en_pantalla("Discapacitado se fue sin ser atendido (-4)", 2)

    # Si ya se llegó a la mitad de penalizaciones
    if penalizaciones_discapacitados >= max(1, total_discapacitados // 2):
        if random.random() < 0.82:
            denuncias += 1
            puntos -= 15
            mostrar_mensaje_en_pantalla("¡Demanda! El elevador pierde 15 puntos por no atender discapacitados", 3)

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
    global total_personas_inicial, tiempo_inicio_juego
    
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

    global personas_lobby, posiciones_personas_lobby, persona_seleccionada_lobby, total_personas_inicial
    personas_lobby = generar_personas_lobby()
    total_personas_inicial = len(personas_lobby)
    posiciones_personas_lobby = distribuir_personas_lobby(personas_lobby)
    persona_seleccionada_lobby = 0
    tiempo_inicio_juego = time.time()

def generar_personas_lobby():
    global total_discapacitados
    global total_trabajadores
    global total_discapacitados_generados  # <-- Agrega esta línea
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
        # Iniciar temporizador si es trabajador
        if isinstance(p, PersonaTrabajador):
            p.iniciar_temporizador()
            total_trabajadores += 1
        # Contar discapacitados generados
        if isinstance(p, PersonaDiscapacitada):
            total_discapacitados_generados += 1
        personas.append(p)
    
    # Calcular el límite de mala reputación (65% del total de trabajadores)
    global limite_mala_reputacion
    limite_mala_reputacion = max(1, int(total_trabajadores * 0.65))
    
    print(f"Total de trabajadores: {total_trabajadores}")
    print(f"Límite de mala reputación (65%): {limite_mala_reputacion}")
    print(f"Total de discapacitados generados: {total_discapacitados_generados}")
    
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
            global puntos, penalizaciones_discapacitados, denuncias
            
            # Aplicar penalización base de -5 puntos
            puntos -= 5
            mostrar_mensaje_en_pantalla("¡PENALIZACIÓN! -5 puntos por no subir un discapacitado", 3)
            print("⚠️ PENALIZACIÓN: No había discapacitados en el elevador (-5 puntos)")
            
            # Incrementar el contador de penalizaciones para el sistema de denuncias
            penalizaciones_discapacitados += 1
            
            # Verificar si se debe aplicar una denuncia
            if penalizaciones_discapacitados >= max(1, total_discapacitados_generados // 2):
                if random.random() < 0.82:  # 82% de probabilidad
                    puntos -= 15
                    denuncias += 1
                    mensaje = "¡DEMANDA! -15 puntos por no atender suficientes discapacitados"
                    mensaje += f" | Penalizaciones: {penalizaciones_discapacitados}/{total_discapacitados_generados}"
                    mostrar_mensaje_en_pantalla(mensaje, 3)
                    print(f"⚖️ DEMANDA: Penalizaciones {penalizaciones_discapacitados} de {total_discapacitados_generados}")
    
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
    global mensaje_temporal, tiempo_mensaje, game_over, total_personas_inicial, tiempo_inicio_juego
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
                    # Al regresar al lobby, si el lobby y el elevador están vacíos, mostrar completado
                    if len(personas_lobby) == 0 and elevador and hasattr(elevador, 'personas_dentro') and len(elevador.personas_dentro) == 0 and not game_over:
                        game_over = True
                        contexto = {
                            "screen": screen,
                            "fuente_led": pygame.font.SysFont("Courier New", 48, bold=True),
                            "ANCHO": ANCHO,
                            "ALTO": ALTO,
                            "COLORES": COLORES,
                            "clock": pygame.time.Clock()
                        }
                        personas_atendidas = total_personas_inicial
                        porcentaje = 100  # 100% porque todas las personas fueron atendidas
                        tiempo_total = int(time.time() - tiempo_inicio_juego)
                        minutos = tiempo_total // 60
                        segundos = tiempo_total % 60
                        tiempo_str = f"Tiempo: {minutos:02d}:{segundos:02d}"
                        resultado = mostrar_pantalla_final(contexto, 'completado', porcentaje, tiempo_str)
                        if resultado == "menu":
                            volver_al_menu_principal()
                        elif resultado == "salir":
                            import sys
                            sys.exit()
                        ejecutando = False
                        return

        # Manejar Game Over por reputación
        if game_over:
            personas_atendidas = total_personas_inicial - len(personas_lobby)
            porcentaje = 0
            if total_personas_inicial > 0:
                porcentaje = int((personas_atendidas / total_personas_inicial) * 100)
            tiempo_total = int(time.time() - tiempo_inicio_juego)
            minutos = tiempo_total // 60
            segundos = tiempo_total % 60
            tiempo_str = f"Tiempo: {minutos:02d}:{segundos:02d}"
            contexto = {
                "screen": screen,
                "fuente_led": pygame.font.SysFont("Courier New", 48, bold=True),
                "ANCHO": ANCHO,
                "ALTO": ALTO,
                "COLORES": COLORES,
                "clock": pygame.time.Clock()
            }
            tipo_final = 'completado' if porcentaje > 50 else 'gameover'
            resultado = mostrar_pantalla_final(contexto, tipo_final, porcentaje, tiempo_str)
            if resultado == "menu":
                volver_al_menu_principal()
            elif resultado == "salir":
                import sys
                sys.exit()
            ejecutando = False
            return

        # Actualizar estado del lobby (incluyendo trabajadores enojados)
        if estado_juego["modo"] == "lobby" and not game_over:
            actualizar_estado_lobby()
            
            # Ya no se verifica victoria aquí, solo cuando el ascensor y el lobby estén vacíos

            # Verificar temporizador de gameplay
            if temporizador_gameplay:
                terminado = temporizador_gameplay.actualizar()
                if terminado:
                    mostrar_mensaje_en_pantalla("¡Tiempo agotado! Fin del juego.", 2)
                    pygame.display.flip()
                    pygame.time.wait(1000)
                    # Mostrar pantalla de Game Over y esperar tecla
                    contexto = {
                        "screen": screen,
                        "fuente_led": pygame.font.SysFont("Courier New", 48, bold=True),
                        "ANCHO": ANCHO,
                        "ALTO": ALTO,
                        "COLORES": COLORES,
                        "clock": pygame.time.Clock()
                    }
                    # Calcular porcentaje y tiempo
                    personas_atendidas = total_personas_inicial - len(personas_lobby)
                    porcentaje = 0
                    if total_personas_inicial > 0:
                        porcentaje = int((personas_atendidas / total_personas_inicial) * 100)
                    tiempo_total = int(time.time() - tiempo_inicio_juego)
                    minutos = tiempo_total // 60
                    segundos = tiempo_total % 60
                    tiempo_str = f"Tiempo: {minutos:02d}:{segundos:02d}"
                    contexto = {
                        "screen": screen,
                        "fuente_led": pygame.font.SysFont("Courier New", 48, bold=True),
                        "ANCHO": ANCHO,
                        "ALTO": ALTO,
                        "COLORES": COLORES,
                        "clock": pygame.time.Clock()
                    }
                    resultado = mostrar_pantalla_final(contexto, 'gameover', porcentaje, tiempo_str)
                    if resultado == "menu":
                        volver_al_menu_principal()
                    elif resultado == "salir":
                        import sys
                        sys.exit()
                    ejecutando = False
                    return
            
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

def mostrar_pantalla_gameover_denuncias(contexto, porcentaje, tiempo_str):
    """Muestra la pantalla de Game Over por denuncias y abre el enlace de la ley de igualdad"""
    screen = contexto["screen"]
    fuente_led = contexto["fuente_led"]
    ANCHO = contexto["ANCHO"]
    ALTO = contexto["ALTO"]
    COLORES = contexto["COLORES"]
    # Usa fuente más pequeña para el mensaje de denuncia
    fuente_pequena = contexto.get("fuente_pequena", pygame.font.SysFont("Courier New", 22, bold=True))

    # Cargar imagen de fondo de game over
    try:
        fondo_img = pygame.image.load("assets/gameover.png").convert()
        fondo_img = pygame.transform.scale(fondo_img, (ANCHO, ALTO))
    except Exception as e:
        fondo_img = pygame.Surface((ANCHO, ALTO))
        fondo_img.fill((0, 0, 0))

    screen.blit(fondo_img, (0, 0))

    mensaje1 = "Has perdido, recibiste dos denuncias"
    mensaje2 = "por discriminación."
    mensaje3 = f"Personas atendidas: {porcentaje}%"
    mensaje4 = tiempo_str

    # Mensaje de denuncia en fuente pequeña
    text1 = fuente_pequena.render(mensaje1, True, COLORES["error"])
    text2 = fuente_pequena.render(mensaje2, True, COLORES["error"])
    # Estadísticas en fuente grande
    text3 = fuente_led.render(mensaje3, True, COLORES["texto_activo"])
    text4 = fuente_led.render(mensaje4, True, COLORES["texto_activo"])

    y_centro = ALTO // 2
    # Mensaje de derrota en dos líneas, más abajo para evitar los bordes
    screen.blit(text1, (ANCHO // 2 - text1.get_width() // 2, y_centro + 30))
    screen.blit(text2, (ANCHO // 2 - text2.get_width() // 2, y_centro + 65))
    # Estadísticas debajo
    screen.blit(text3, (ANCHO // 2 - text3.get_width() // 2, y_centro + 120))
    screen.blit(text4, (ANCHO // 2 - text4.get_width() // 2, y_centro + 180))
    pygame.display.flip()

    # Esperar 5.5 segundos
    pygame.time.wait(5500)

    # Abrir el enlace de la ley de igualdad de oportunidades
    webbrowser.open("https://www.tse.go.cr/pdf/normativa/leyigualdaddeoportunidades.pdf")

def actualizar_estado_lobby():
    """Actualiza el estado del lobby, incluyendo la verificación de trabajadores enojados y denuncias"""
    global personas_lobby, posiciones_personas_lobby, persona_seleccionada_lobby, puntos, mala_reputacion, game_over
    global denuncias

    hay_discapacitados = any(isinstance(p, PersonaDiscapacitada) for p in personas_lobby)
    if denuncias >= 2 and not game_over and hay_discapacitados:
        game_over = True
        # Mostrar pantalla especial de game over por denuncias
        personas_atendidas = total_personas_inicial - len(personas_lobby)
        porcentaje = 0
        if total_personas_inicial > 0:
            porcentaje = int((personas_atendidas / total_personas_inicial) * 100)
        tiempo_total = int(time.time() - tiempo_inicio_juego)
        minutos = tiempo_total // 60
        segundos = tiempo_total % 60
        tiempo_str = f"Tiempo: {minutos:02d}:{segundos:02d}"
        contexto = {
            "screen": screen,
            "fuente_led": pygame.font.SysFont("Courier New", 48, bold=True),
            "ANCHO": ANCHO,
            "ALTO": ALTO,
            "COLORES": COLORES,
        }
        mostrar_pantalla_gameover_denuncias(contexto, porcentaje, tiempo_str)
        return

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

    denuncias_txt = f"DENUNCIAS: {denuncias}"
    s = fuente_pequena.render(denuncias_txt, True, COLORES["error"])
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

def mostrar_pantalla_final(contexto, tipo, porcentaje, tiempo_str, por_denuncias=False):
    import pygame
    import sys

    screen = contexto["screen"]
    ANCHO = contexto["ANCHO"]
    ALTO = contexto["ALTO"]
    clock = contexto["clock"]

    # Cargar la imagen correspondiente
    if tipo == 'completado':
        img_path = "assets/completado.png"
    else:
        img_path = "assets/gameover.png"
    try:
        fondo_img = pygame.image.load(img_path).convert_alpha()
        fondo_img = pygame.transform.scale(fondo_img, (ANCHO, ALTO))
    except Exception as e:
        print(f"[ERROR] No se pudo cargar {img_path}: {e}")
        return

    # Botón izquierdo: Volver al menú principal
    rect_menu = pygame.Rect(110, 505, 360, 55)
    # Botón derecho: Salir
    rect_salir = pygame.Rect(545, 505, 275, 55)

    # Texto de resultado
    font = pygame.font.SysFont(None, 60)
    if porcentaje >= 90:
        txt_result = font.render(f"Éxito ALTO ({porcentaje}%)", True, (0, 255, 0))
    elif porcentaje > 50:
        txt_result = font.render(f"Éxito MEDIO ({porcentaje}%)", True, (255, 255, 0))
    else:
        txt_result = font.render(f"Fracaso ({porcentaje}%)", True, (255, 0, 0))
    txt_tiempo = font.render(tiempo_str, True, (255, 255, 255))

    # Fuente pequeña para el mensaje de denuncia
    fuente_pequena = pygame.font.SysFont("Courier New", 22, bold=True)

    esperando = True
    while esperando:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                esperando = False
                sys.exit()
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    esperando = False
                    return "menu"
            elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                mouse_pos = pygame.mouse.get_pos()
                if rect_menu.collidepoint(mouse_pos):
                    esperando = False
                    return "menu"
                elif rect_salir.collidepoint(mouse_pos):
                    esperando = False
                    sys.exit()

        screen.blit(fondo_img, (0, 0))
        # Centrar los textos en la pantalla
        screen.blit(
            txt_result,
            (ANCHO // 2 - txt_result.get_width() // 2, ALTO // 2 - txt_result.get_height())
        )
        screen.blit(
            txt_tiempo,
            (ANCHO // 2 - txt_tiempo.get_width() // 2, ALTO // 2 + 10)
        )

        # Si fue por denuncias, mostrar el mensaje en dos líneas debajo del tiempo, en fuente pequeña y color de error
        if por_denuncias:
            mensaje1 = "Has perdido, recibiste dos denuncias"
            mensaje2 = "por discriminación."
            text1 = fuente_pequena.render(mensaje1, True, (255, 50, 50))
            text2 = fuente_pequena.render(mensaje2, True, (255, 50, 50))
            y_base = ALTO // 2 + 80
            screen.blit(text1, (ANCHO // 2 - text1.get_width() // 2, y_base))
            screen.blit(text2, (ANCHO // 2 - text2.get_width() // 2, y_base + 30))

        pygame.display.flip()
        clock.tick(30)
