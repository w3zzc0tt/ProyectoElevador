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
evento_enviado = False  # Previene múltiples eventos USEREVENT+10
orden_pisos_destino = []
indice_piso_destino = 0

# Recursos
fondo_pisos = None
ascensor_img = None
ascensor_tamano = (96, 94)
ascensor_pos = (385, 485)  # Posición inicial en el lobby

# Contexto desde main
elevador = None
volver_al_menu_principal = None
COLORES = None
fuente_pequena = None
PersonaDiscapacitada = None
PersonaObesa = None
PersonaTrabajador = None
PersonaCliente = None

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
    global PersonaDiscapacitada, PersonaObesa, PersonaTrabajador, PersonaCliente
    
    elevador = getattr(modulo_main, 'elevador', None)
    volver_al_menu_principal = getattr(modulo_main, 'volver_al_menu_principal', None)
    COLORES = getattr(modulo_main, 'COLORES', None)
    fuente_pequena = getattr(modulo_main, 'fuente_pequena', None)
    
    # Importar las clases de personas
    PersonaDiscapacitada = getattr(modulo_main, 'PersonaDiscapacitada', None)
    PersonaObesa = getattr(modulo_main, 'PersonaObesa', None)
    PersonaTrabajador = getattr(modulo_main, 'PersonaTrabajador', None)
    PersonaCliente = getattr(modulo_main, 'PersonaCliente', None)

def determinar_orden_pisos_destino():
    """Determina el orden óptimo de los pisos destino basado en la prioridad de las personas"""
    # Crear listas separadas por prioridad
    pisos_discapacitados = []
    pisos_obesos = []
    pisos_trabajadores = []
    pisos_clientes = []
    
    # Clasificar los pisos destino por prioridad
    for persona in personas_en_ascensor:
        if hasattr(persona, 'piso_destino'):
            if isinstance(persona, PersonaDiscapacitada):
                pisos_discapacitados.append(persona.piso_destino)
            elif isinstance(persona, PersonaObesa):
                pisos_obesos.append(persona.piso_destino)
            elif isinstance(persona, PersonaTrabajador):
                pisos_trabajadores.append(persona.piso_destino)
            elif isinstance(persona, PersonaCliente):
                pisos_clientes.append(persona.piso_destino)
    
    # Ordenar cada lista de pisos
    pisos_discapacitados.sort()
    pisos_obesos.sort()
    pisos_trabajadores.sort()
    pisos_clientes.sort()
    
    # Determinar el orden de los pisos destino
    orden_pisos = []
    
    # 1. Personas discapacitadas (máxima prioridad)
    for piso in pisos_discapacitados:
        if piso not in orden_pisos:
            orden_pisos.append(piso)
    
    # 2. Personas obesas (segunda prioridad)
    for piso in pisos_obesos:
        if piso not in orden_pisos:
            orden_pisos.append(piso)
    
    # 3. Trabajadores (tercera prioridad)
    for piso in pisos_trabajadores:
        if piso not in orden_pisos:
            orden_pisos.append(piso)
    
    # 4. Clientes (mínima prioridad)
    for piso in pisos_clientes:
        if piso not in orden_pisos:
            orden_pisos.append(piso)
    
    # Si no hay pisos destino, añadir uno aleatorio
    if not orden_pisos:
        orden_pisos = [random.randint(1, 4)]
    
    return orden_pisos

def asignar_pisos_destino():
    """Asigna un piso destino aleatorio a cada persona en el ascensor"""
    for persona in personas_en_ascensor:
        # Pisos del 1 al 4
        persona.piso_destino = random.randint(1, 4)

def iniciar_ascensor(contexto):
    global elevador, volver_al_menu_principal, COLORES, fuente_pequena
    global personas_en_ascensor, piso_actual, subiendo, bajando
    global esperando_en_piso, tiempo_ultimo_piso, sprite_cargado, personas_saliendo
    global orden_pisos_destino, indice_piso_destino, evento_enviado

    elevador = contexto['elevador']
    volver_al_menu_principal = contexto['volver_al_menu_principal']
    COLORES = contexto['COLORES']
    fuente_pequena = contexto['fuente_pequena']
    
    # Importar las clases de personas del contexto
    global PersonaDiscapacitada, PersonaObesa, PersonaTrabajador, PersonaCliente
    PersonaDiscapacitada = contexto['PersonaDiscapacitada']
    PersonaObesa = contexto['PersonaObesa']
    PersonaTrabajador = contexto['PersonaTrabajador']
    PersonaCliente = contexto['PersonaCliente']

    personas_en_ascensor = elevador.personas_dentro.copy()
    elevador.personas_dentro.clear()
    elevador.area_ocupada = 0

    # Asignar piso destino a cada persona
    asignar_pisos_destino()
    
    # Determinar el orden de los pisos destino
    orden_pisos_destino = determinar_orden_pisos_destino()
    indice_piso_destino = 0
    
    piso_actual = 0
    esperando_en_piso = False
    personas_saliendo.clear()
    tiempo_ultimo_piso = pygame.time.get_ticks()
    cargar_sprites()
    sprite_cargado = True
    evento_enviado = False  # Reiniciar para que funcione correctamente cada vez
    
    # Determinar dirección inicial
    if orden_pisos_destino and orden_pisos_destino[0] > piso_actual:
        subiendo = True
        bajando = False
    else:
        subiendo = False
        bajando = True

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
    global orden_pisos_destino, indice_piso_destino, evento_enviado

    ahora = pygame.time.get_ticks()

    # Si no hay más personas en el ascensor y estamos de vuelta en el lobby
    if not personas_en_ascensor and piso_actual == 0:
        if not evento_enviado:
            pygame.event.post(pygame.event.Event(pygame.USEREVENT + 10))
            evento_enviado = True
        return

    if esperando_en_piso:
        if ahora - tiempo_ultimo_piso >= tiempo_espera_piso:
            esperando_en_piso = False
            tiempo_ultimo_piso = ahora
            
            # Verificar si es el piso destino actual
            if indice_piso_destino < len(orden_pisos_destino) and piso_actual == orden_pisos_destino[indice_piso_destino]:
                # Descargar personas para este piso
                personas_a_bajar = [p for p in personas_en_ascensor if hasattr(p, 'piso_destino') and p.piso_destino == piso_actual]
                for persona in personas_a_bajar:
                    if hasattr(persona, 'cargar_imagen'):
                        persona.cargar_imagen()
                    personas_en_ascensor.remove(persona)
                    
                    # Añadir a personas_saliendo para animación
                    x_inicio, y_inicio = pisos_posiciones[piso_actual]
                    direccion = "izquierda" if piso_actual in [1, 3] else "derecha"
                    offset_x = len(personas_saliendo) * 70 if direccion == "derecha" else -len(personas_saliendo) * 70
                    personas_saliendo.append({
                        "sprite": persona.imagen,
                        "x": x_inicio + 10 + offset_x,
                        "y": y_inicio + 20,
                        "direccion": direccion,
                        "velocidad": 2
                    })
                
                # Incrementar índice de piso destino
                indice_piso_destino += 1
    
    if not esperando_en_piso:
        if ahora - tiempo_ultimo_piso >= 1500:
            # Determinar si hay más pisos destino
            if indice_piso_destino < len(orden_pisos_destino):
                piso_destino = orden_pisos_destino[indice_piso_destino]
                
                # Mover hacia el piso destino
                if piso_actual < piso_destino:
                    piso_actual += 1
                    subiendo = True
                    bajando = False
                elif piso_actual > piso_destino:
                    piso_actual -= 1
                    subiendo = False
                    bajando = True
                else:
                    # Llegamos al piso destino
                    esperando_en_piso = True
                    tiempo_ultimo_piso = ahora
            else:
                # No hay más pisos destino, regresar al lobby
                if piso_actual > 0:
                    piso_actual -= 1
                    subiendo = False
                    bajando = True
                else:
                    # Ya estamos en el lobby
                    if not evento_enviado:
                        pygame.event.post(pygame.event.Event(pygame.USEREVENT + 10))
                        evento_enviado = True
            tiempo_ultimo_piso = ahora

def dibujar_pisos(screen):
    print("🏗️ DIBUJANDO ASCENSOR")
    if not sprite_cargado:
        cargar_sprites()
        # No returns aquí: seguimos para dibujar

    screen.fill((0, 0, 0))  # Fondo negro

    if fondo_pisos:
        screen.blit(fondo_pisos, (0, 0))

    # Determinar posición del ascensor
    if piso_actual < len(pisos_posiciones):
        x_ascensor, y_ascensor = pisos_posiciones[piso_actual]
    else:
        x_ascensor, y_ascensor = ascensor_pos

    # Dibujar el ascensor
    if ascensor_img:
        screen.blit(ascensor_img, (x_ascensor, y_ascensor))

    # Mostrar información del piso y personas
    fuente = pygame.font.SysFont("Courier New", 24, bold=True)
    piso_txt = fuente.render(f"Piso {piso_actual}", True, (255, 255, 255))
    personas_txt = fuente.render(f"Personas restantes: {len(personas_en_ascensor)}", True, (255, 255, 255))
    screen.blit(piso_txt, (20, 20))
    screen.blit(personas_txt, (20, 50))

    # Mostrar orden de los pisos destino
    if orden_pisos_destino:
        orden_txt = "Orden: " + " → ".join(str(p) for p in orden_pisos_destino[indice_piso_destino:])
        orden_surface = fuente_pequena.render(orden_txt, True, (0, 255, 0))
        screen.blit(orden_surface, (20, 80))
    
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