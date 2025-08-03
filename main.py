import pygame
import sys
import os
import random
import time
from enum import Enum
from threading import Thread, Event

pygame.init()

# Asegura que el script trabaje desde su directorio
script_dir = os.path.dirname(os.path.abspath(__file__))
os.chdir(script_dir)

# Tamaño de la pantalla
ANCHO, ALTO = 900, 600
screen = pygame.display.set_mode((ANCHO, ALTO))
pygame.display.set_caption("Panel de Ascensor")

# Cargar imagen de fondo con manejo de errores mejorado
fondo = None
fondo_pos_x, fondo_pos_y = 0, 0
try:
    ruta_imagen = os.path.join("assets", "elevator.jpg")
    print("Intentando cargar imagen desde:", os.path.abspath(ruta_imagen))
    fondo_original = pygame.image.load(ruta_imagen)
    rel_ancho = ANCHO / fondo_original.get_width()
    rel_alto = ALTO / fondo_original.get_height()
    escala = max(rel_ancho, rel_alto)
    nuevo_ancho = int(fondo_original.get_width() * escala)
    nuevo_alto = int(fondo_original.get_height() * escala)
    fondo = pygame.transform.scale(fondo_original, (nuevo_ancho, nuevo_alto))
    fondo_pos_x = (ANCHO - nuevo_ancho) // 2
    fondo_pos_y = (ALTO - nuevo_alto) // 2
except Exception as e:
    print(f"Error cargando imagen de fondo: {e}")

# Cargar imagen de fondo del lobby
fondo_lobby = None
fondo_pos_x_lobby, fondo_pos_y_lobby = 0, 0
try:
    ruta_imagen_lobby = os.path.join("assets", "lobby.png")
    print("Intentando cargar imagen de lobby desde:", os.path.abspath(ruta_imagen_lobby))
    fondo_lobby_original = pygame.image.load(ruta_imagen_lobby)
    rel_ancho_lobby = ANCHO / fondo_lobby_original.get_width()
    rel_alto_lobby = ALTO / fondo_lobby_original.get_height()
    escala_lobby = max(rel_ancho_lobby, rel_alto_lobby)
    nuevo_ancho_lobby = int(fondo_lobby_original.get_width() * escala_lobby)
    nuevo_alto_lobby = int(fondo_lobby_original.get_height() * escala_lobby)
    fondo_lobby = pygame.transform.scale(fondo_lobby_original, (nuevo_ancho_lobby, nuevo_alto_lobby))
    fondo_pos_x_lobby = (ANCHO - nuevo_ancho_lobby) // 2
    fondo_pos_y_lobby = (ALTO - nuevo_alto_lobby) // 2
except Exception as e:
    print(f"Error cargando imagen de fondo del lobby: {e}")

# Superficie oscura para el panel (solo para estados de menu)
panel_surface_oscura = pygame.Surface((ANCHO, ALTO), pygame.SRCALPHA)
panel_surface_oscura.fill((0, 0, 0, 140)) # Negro semitransparente

# Cargar imágenes de personajes
imagenes_personas = {}
nombres_imagenes = {
    "Cliente": "cliente1.png",
    "Trabajador": "trabajador1.png",
    "Obeso": "gordomorbido.png",
    "Discapacitado": "discapacitado1.png"
}
for tipo, nombre_archivo in nombres_imagenes.items():
    try:
        ruta_img_persona = os.path.join("assets", nombre_archivo)
        print(f"Intentando cargar imagen para {tipo} desde: {os.path.abspath(ruta_img_persona)}")
        img = pygame.image.load(ruta_img_persona).convert_alpha()
        # Escalar la imagen a un tamaño razonable, por ejemplo 60x60
        imagenes_personas[tipo] = pygame.transform.scale(img, (60, 60))
    except Exception as e:
        print(f"Error cargando imagen para {tipo}: {e}")
        imagenes_personas[tipo] = None # O una imagen por defecto si se desea

COLORES = {
    "fondo": (30, 30, 40),
    "panel_exterior": (50, 50, 60, 180),
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
    "advertencia": (255, 200, 0),
    "error": (255, 50, 50),
    "exito": (50, 255, 50)
}

fuente = pygame.font.SysFont("Courier New", 32, bold=True)
fuente_led = pygame.font.SysFont("Courier New", 48, bold=True)
fuente_pequena = pygame.font.SysFont("Courier New", 24)
fuente_mediana = pygame.font.SysFont("Courier New", 28)

class Dificultad(Enum):
    FACIL = 1
    NORMAL = 2
    DIFICIL = 3

class Persona:
    def __init__(self, tipo, nombre="Persona"):
        self.tipo = tipo
        self.nombre = nombre
        self.area_ocupada = 0
        self.prioritario = False
        self.puede_esperar = False
        # Asignar la imagen correspondiente
        self.imagen = imagenes_personas.get(self.tipo, None)

    def __str__(self):
        return f"{self.nombre} ({self.tipo})"

class PersonaDiscapacitada(Persona):
    def __init__(self, nombre="Persona Discapacitada"):
        super().__init__("Discapacitado", nombre)
        self.area_ocupada = 2
        self.prioritario = True
        self.puede_esperar = True

class PersonaObesa(Persona):
    def __init__(self, nombre="Persona Obesa", peso=None):
        super().__init__("Obeso", nombre)
        self.peso = peso or random.randint(120, 150)
        self.area_ocupada = 4
        self.prioritario = False
        self.puede_esperar = False

class PersonaTrabajador(Persona):
    def __init__(self, nombre="Trabajador"):
        super().__init__("Trabajador", nombre)
        self.area_ocupada = 1
        self.prioritario = False
        self.puede_esperar = False
        self.tiempo_maximo = 75  # 1 minuto y 15 segundos
        self.tiempo_advertencia = 30  # 30 segundos antes de irse
        self.tiempo_restante = self.tiempo_maximo
        self.evento_tiempo = Event()
        self.thread_tiempo = None
        self.se_fue = False

    def iniciar_contador(self, juego_modulo):
        """Inicia el contador de tiempo del trabajador.
           juego_modulo: Referencia al módulo del juego para acceder a funciones globales."""
        def contar_tiempo():
            while self.tiempo_restante > 0 and not self.evento_tiempo.is_set():
                time.sleep(1)
                self.tiempo_restante -= 1
                # Mostrar advertencia cuando queden 30 segundos
                if self.tiempo_restante == self.tiempo_advertencia:
                    juego_modulo.mostrar_advertencia(f"¡Advertencia! {self.nombre} se irá en {self.tiempo_advertencia} segundos")
                # Si se acaba el tiempo, el trabajador se va
                if self.tiempo_restante <= 0 and not self.evento_tiempo.is_set():
                    self.se_fue = True
                    juego_modulo.trabajador_se_fue(self)
        self.thread_tiempo = Thread(target=contar_tiempo)
        self.thread_tiempo.daemon = True
        self.thread_tiempo.start()

    def detener_contador(self):
        """Detiene el contador del trabajador"""
        if self.thread_tiempo:
            self.evento_tiempo.set()
            self.thread_tiempo.join()

class PersonaCliente(Persona):
    def __init__(self, nombre="Cliente"):
        super().__init__("Cliente", nombre)
        self.area_ocupada = 1
        self.prioritario = False
        self.puede_esperar = True

class Elevador: # Mantenido por compatibilidad, aunque simplificado para el lobby
    def __init__(self, capacidad_area=9):  # Máximo 9 áreas
        self.capacidad_area = capacidad_area
        self.area_ocupada = 0
        self.personas_dentro = []

    def puede_entrar(self, persona):
        """Verifica si una persona puede entrar al elevador"""
        return (self.area_ocupada + persona.area_ocupada) <= self.capacidad_area

    def entrar_persona(self, persona):
        """Agrega una persona al elevador"""
        if self.puede_entrar(persona):
            self.personas_dentro.append(persona)
            self.area_ocupada += persona.area_ocupada
            return True
        return False

    def salir_persona(self, persona):
        """Saca una persona del elevador"""
        if persona in self.personas_dentro:
            self.personas_dentro.remove(persona)
            self.area_ocupada -= persona.area_ocupada
            return True
        return False

# Estados del menú
MENU_PRINCIPAL = 0
MENU_DIFICULTAD = 1
MENU_CONFIG = 2
MENU_SALIR = 3
# Eliminado MENU_JUEGO y MENU_PAUSA ya que no se usan
LOBBY = 4  # Nuevo estado para el lobby
estado_actual = MENU_PRINCIPAL

# Menús simplificados ya que MENU_JUEGO y MENU_PAUSA ya no existen
menus = {
    MENU_PRINCIPAL: ["1. Jugar", "2. Config", "3. Salir"],
    MENU_DIFICULTAD: ["1. Fácil", "2. Normal", "3. Difícil", "4. Volver"],
    MENU_CONFIG: ["1. Volumen", "2. Shake [ON/OFF]", "3. Volver"],
    MENU_SALIR: ["1. Salir", "2. Cancelar"]
    # LOBBY no necesita menú
}

panel_width, panel_height = 400, 440
panel_left = (ANCHO - panel_width) // 2
panel_top = (ALTO - panel_height) // 2
ascensor_width, ascensor_height = 24, 24
ascensor_x = panel_left - 40
ascensor_y = panel_top + 40
ascensor_color = COLORES["ascensor"]
opcion_seleccionada = 0
ascensor_target_y = ascensor_y
clock = pygame.time.Clock()

# Variables del juego
dificultad_actual = Dificultad.NORMAL
elevador = Elevador(9) # Se crea un elevador para el lobby
mensaje_temporal = ""
tiempo_mensaje = 0

# Variables para el lobby
personas_lobby = []
posiciones_personas_lobby = []
persona_seleccionada_lobby = 0

def volver_al_menu_principal():
    global estado_actual, opcion_seleccionada, elevador
    estado_actual = MENU_PRINCIPAL
    opcion_seleccionada = 0
    elevador = Elevador(9) # Reiniciar elevador

def obtener_total_personas(dificultad):
    """Obtiene el total de personas según la dificultad"""
    totales = {
        Dificultad.FACIL: 25,
        Dificultad.NORMAL: 35,
        Dificultad.DIFICIL: 40
    }
    return totales[dificultad]

def obtener_limite_obesos(dificultad):
    """Obtiene el límite de personas obesas según la dificultad"""
    limites = {
        Dificultad.FACIL: 2,
        Dificultad.NORMAL: 3,
        Dificultad.DIFICIL: random.randint(4, 5)
    }
    return limites[dificultad]

def crear_persona_aleatoria():
    """Crea una persona aleatoria según las probabilidades"""
    # Simplificado para el lobby, sin lógica de conteo de obesos compleja
    tipos = [
        PersonaDiscapacitada,
        PersonaObesa,
        PersonaTrabajador,
        PersonaCliente
    ]
    tipo_seleccionado = random.choice(tipos)
    return tipo_seleccionado()

def generar_personas_lobby(dificultad):
    """Genera un grupo de personas para el lobby según la dificultad"""
    personas = []
    limite_obesos = obtener_limite_obesos(dificultad)
    total_personas = obtener_total_personas(dificultad)
    obesos_creados = 0

    # Generar personas hasta alcanzar el total
    while len(personas) < total_personas:
        nueva_persona = crear_persona_aleatoria()
        
        # Verificar límite de obesos
        if isinstance(nueva_persona, PersonaObesa):
            if obesos_creados >= limite_obesos:
                # Si ya se alcanzó el límite, crear otro tipo de persona
                # Esto evita el bucle infinito si no se pueden crear más personas
                tipos_alternativos = [PersonaDiscapacitada, PersonaTrabajador, PersonaCliente]
                tipo_alternativo = random.choice(tipos_alternativos)
                nueva_persona = tipo_alternativo()
            else:
                obesos_creados += 1
                
        personas.append(nueva_persona)

    return personas

def distribuir_personas_lobby(personas):
    """Distribuye las personas en el suelo del lobby (forma de trapecio) sin solaparse ni chocar visualmente."""
    posiciones = []
    intentos_maximos = 100

    # Límites del área del suelo (ajusta si tu imagen cambia)
    y_min = ALTO // 2 + 50      # Parte superior del suelo
    y_max = ALTO - 110          # Parte inferior del suelo
    x_min_global = 50           # Borde izquierdo
    x_max_global = ANCHO - 110  # Borde derecho

    # Tamaño de la imagen de persona (60x60)
    ancho_persona = 60
    alto_persona = 60

    for _ in personas:
        intentos = 0
        while intentos < intentos_maximos:
            # Elegir y aleatorio en el rango del suelo
            y = random.randint(y_min, y_max)

            # Calcular el ancho disponible en esa altura (efecto trapecio)
            proporcion = (y - y_min) / (y_max - y_min)  # 0 = arriba, 1 = abajo
            ancho_minimo = 400  # Ancho en la parte superior del trapecio
            ancho_total = x_max_global - x_min_global
            ancho_actual = ancho_minimo + proporcion * (ancho_total - ancho_minimo)

            # Calcular márgenes para centrar el rango
            margen = (ancho_total - ancho_actual) / 2
            x_min_local = x_min_global + margen
            x_max_local = x_max_global - margen

            # Generar x dentro del rango ajustado
            x = random.randint(int(x_min_local), int(x_max_local))

            # Crear un rectángulo para la nueva persona (con un pequeño margen extra si se quiere más separación)
            nuevo_rect = pygame.Rect(x, y, ancho_persona, alto_persona)

            # Verificar colisión con personas ya colocadas
            solapa = False
            for px, py in posiciones:
                existente_rect = pygame.Rect(px, py, ancho_persona, alto_persona)
                if nuevo_rect.colliderect(existente_rect):
                    solapa = True
                    break

            if not solapa:
                posiciones.append((x, y))
                break
            intentos += 1

        # Fallback: si no se encontró lugar, colocar igual (última posición)
        if intentos >= intentos_maximos:
            posiciones.append((x, y))

    return posiciones

def mostrar_mensaje_temporal(mensaje, color="exito"):
    global mensaje_temporal, tiempo_mensaje
    mensaje_temporal = mensaje
    tiempo_mensaje = time.time() + 3  # Mostrar por 3 segundos

def seleccionar_persona_lobby():
    """Selecciona una persona del lobby para subir al elevador"""
    global personas_lobby, posiciones_personas_lobby, persona_seleccionada_lobby, elevador
    
    if personas_lobby and len(personas_lobby) > 0:
        persona = personas_lobby[persona_seleccionada_lobby]
        
        # Verificar si puede entrar al elevador
        if elevador.puede_entrar(persona):
            # Agregar persona al elevador
            if elevador.entrar_persona(persona):
                # Remover la persona seleccionada del lobby
                personas_lobby.pop(persona_seleccionada_lobby)
                posiciones_personas_lobby.pop(persona_seleccionada_lobby)
                
                # Ajustar índice de selección
                if persona_seleccionada_lobby >= len(personas_lobby) and len(personas_lobby) > 0:
                    persona_seleccionada_lobby = len(personas_lobby) - 1
                elif len(personas_lobby) == 0:
                    persona_seleccionada_lobby = 0
                    # Si no quedan personas, volver al menú principal
                    mostrar_mensaje_temporal("¡Todas las personas han subido al elevador!", "exito")
                    # En lugar de volver inmediatamente, mostrar el mensaje por un tiempo
                    # Se puede usar un timer o simplemente esperar a que el jugador presione una tecla
                    # Por ahora, simplemente mostramos el mensaje y dejamos que el jugador vuelva con ESC o algo similar
                    # volver_al_menu_principal() # Descomentar si quieres volver automáticamente
                     
                mostrar_mensaje_temporal(f"{persona.nombre} subió al elevador", "exito")
            else:
                mostrar_mensaje_temporal("Error al subir persona", "error")
        else:
            mostrar_mensaje_temporal("No hay espacio suficiente en el elevador", "error")

def mostrar_contadores_lobby():
    """Muestra los contadores de personas en el lobby"""
    if not personas_lobby:
        return
        
    total_personas = len(personas_lobby)
    trabajadores = sum(1 for p in personas_lobby if isinstance(p, PersonaTrabajador))
    clientes = sum(1 for p in personas_lobby if isinstance(p, PersonaCliente))
    discapacitados = sum(1 for p in personas_lobby if isinstance(p, PersonaDiscapacitada))
    obesos = sum(1 for p in personas_lobby if isinstance(p, PersonaObesa))

    texto_total = f"Personas Restantes: {total_personas}"
    texto_trabajadores = f"Trabajadores: {trabajadores}"
    texto_clientes = f"Clientes: {clientes}"
    texto_discapacitados = f"Discapacitados: {discapacitados}"
    texto_obesos = f"Obesos: {obesos}"

    surface_total = fuente_pequena.render(texto_total, True, COLORES["texto_activo"])
    surface_trabajadores = fuente_pequena.render(texto_trabajadores, True, COLORES["texto_activo"])
    surface_clientes = fuente_pequena.render(texto_clientes, True, COLORES["texto_activo"])
    surface_discapacitados = fuente_pequena.render(texto_discapacitados, True, COLORES["texto_activo"])
    surface_obesos = fuente_pequena.render(texto_obesos, True, COLORES["texto_activo"])

    screen.blit(surface_total, (10, 10))
    screen.blit(surface_trabajadores, (10, 40))
    screen.blit(surface_clientes, (10, 70))
    screen.blit(surface_discapacitados, (10, 100))
    screen.blit(surface_obesos, (10, 130))
    
    # Mostrar ocupación del elevador
    texto_elevador = f"Elevador: {elevador.area_ocupada}/9"
    surface_elevador = fuente_pequena.render(texto_elevador, True, COLORES["texto_activo"])
    screen.blit(surface_elevador, (ANCHO - surface_elevador.get_width() - 10, 10))

def iniciar_lobby():
    """Inicia la escena del lobby"""
    global personas_lobby, posiciones_personas_lobby, persona_seleccionada_lobby, estado_actual, elevador
    personas_lobby = generar_personas_lobby(dificultad_actual)
    posiciones_personas_lobby = distribuir_personas_lobby(personas_lobby)
    persona_seleccionada_lobby = 0
    estado_actual = LOBBY
    # Reiniciar elevador para esta sesión del lobby
    elevador = Elevador(9)
    mostrar_mensaje_temporal(f"Lobby cargado - {dificultad_actual.name}", "exito")

def manejar_seleccion():
    global estado_actual, opcion_seleccionada, dificultad_actual
    if estado_actual == MENU_PRINCIPAL:
        if opcion_seleccionada == 0:
            estado_actual = MENU_DIFICULTAD
        elif opcion_seleccionada == 1:
            estado_actual = MENU_CONFIG
        elif opcion_seleccionada == 2:
            estado_actual = MENU_SALIR
        opcion_seleccionada = 0
    elif estado_actual == MENU_DIFICULTAD:
        if opcion_seleccionada == 0:
            dificultad_actual = Dificultad.FACIL
        elif opcion_seleccionada == 1:
            dificultad_actual = Dificultad.NORMAL
        elif opcion_seleccionada == 2:
            dificultad_actual = Dificultad.DIFICIL
        elif opcion_seleccionada == 3:
            volver_al_menu_principal()
            return
        if opcion_seleccionada < 3:
            # Iniciar lobby en lugar del juego original
            iniciar_lobby()
        opcion_seleccionada = 0
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
    # 1. Dibujar fondo
    if estado_actual == LOBBY and fondo_lobby:
        screen.blit(fondo_lobby, (fondo_pos_x_lobby, fondo_pos_y_lobby))
    elif fondo and estado_actual != LOBBY:
        screen.blit(fondo, (fondo_pos_x, fondo_pos_y))
    else:
        screen.fill(COLORES["fondo"])
    
    # Dibujar lobby si es el estado actual
    if estado_actual == LOBBY:
        # Dibujar personas en el lobby
        for i, (x, y) in enumerate(posiciones_personas_lobby):
            if i < len(personas_lobby):  # Verificación de seguridad
                persona = personas_lobby[i]
                if hasattr(persona, 'imagen') and persona.imagen:
                    # Resaltar persona seleccionada
                    if i == persona_seleccionada_lobby:
                        # Dibujar borde resaltado
                        pygame.draw.rect(screen, COLORES["verde_led"], (x-5, y-5, 70, 70), 3, border_radius=10)
                    screen.blit(persona.imagen, (x, y))
        
        # Mostrar contadores
        mostrar_contadores_lobby()
        
        # Mostrar instrucciones
        instrucciones = "Flechas: Mover seleccion | ENTER: Subir al elevador | ESC: Volver al menu"
        instrucciones_surface = fuente_pequena.render(instrucciones, True, COLORES["texto_activo"])
        screen.blit(instrucciones_surface, (ANCHO//2 - instrucciones_surface.get_width()//2, ALTO - 40))
        
        # Mostrar mensaje temporal
        if mensaje_temporal and time.time() < tiempo_mensaje:
            mensaje_surface = fuente_mediana.render(mensaje_temporal, True, COLORES["advertencia"])
            screen.blit(mensaje_surface, (ANCHO // 2 - mensaje_surface.get_width() // 2, 20))
        
        return  # No dibujar el panel en el lobby
    
    # 2. Dibujar panel oscuro (fondo del panel) - solo para estados de menú
    screen.blit(panel_surface_oscura, (0, 0))
    # 3. Dibujar el panel principal
    pygame.draw.rect(screen, COLORES["panel_interior"], (panel_left, panel_top, panel_width, panel_height), border_radius=15)
    pygame.draw.rect(screen, COLORES["borde_panel"], (panel_left, panel_top, panel_width, panel_height), 3, border_radius=15)
    
    # Mostrar mensaje temporal
    if mensaje_temporal and time.time() < tiempo_mensaje:
        mensaje_surface = fuente_mediana.render(mensaje_temporal, True, COLORES["advertencia"])
        screen.blit(mensaje_surface, (ANCHO // 2 - mensaje_surface.get_width() // 2, panel_top - 40))
    # Display del piso/estado (solo en menús)
    display_rect = pygame.Rect(panel_left + 30, panel_top + 30, panel_width - 60, 70)
    pygame.draw.rect(screen, COLORES["display_fondo"], display_rect, border_radius=8)
    pygame.draw.rect(screen, COLORES["display_borde"], display_rect, 2, border_radius=8)
    piso_txt = fuente_led.render(str(opcion_seleccionada + 1), True, COLORES["verde_led"])
    screen.blit(piso_txt, (display_rect.centerx - piso_txt.get_width() // 2, display_rect.centery - piso_txt.get_height() // 2))
    # Opciones del menú
    opciones = menus[estado_actual]
    altura_opcion = 60 if len(opciones) == 4 else 70
    for i, opcion in enumerate(opciones):
        y = panel_top + 120 + i * altura_opcion
        rect_opcion = pygame.Rect(panel_left + 40, y, panel_width - 80, 50)
        if i == opcion_seleccionada:
            pygame.draw.rect(screen, COLORES["opcion_activa"], rect_opcion, border_radius=10)
            pygame.draw.rect(screen, COLORES["borde_opcion"], rect_opcion, 2, border_radius=10)
        else:
            pygame.draw.rect(screen, COLORES["opcion_inactiva"], rect_opcion, border_radius=10)
        color_texto = COLORES["texto_activo"] if i == opcion_seleccionada else COLORES["texto_inactivo"]
        texto = fuente.render(opcion, True, color_texto)
        screen.blit(texto, (rect_opcion.x + 50, rect_opcion.centery - texto.get_height() // 2))
        led_rect = pygame.Rect(rect_opcion.x + 15, rect_opcion.centery - 10, 20, 20)
        pygame.draw.rect(screen, (20, 20, 20), led_rect, border_radius=10)
        if i == opcion_seleccionada:
            pygame.draw.rect(screen, COLORES["verde_led"], led_rect, border_radius=10)
            pygame.draw.rect(screen, COLORES["verde_led_claro"], led_rect, 2, border_radius=10)
    # Ascensor (indicador visual)
    pygame.draw.rect(screen, COLORES["sombra_ascensor"], (ascensor_x - 6, ascensor_y - 6, ascensor_width + 12, ascensor_height + 12), border_radius=8)
    pygame.draw.rect(screen, ascensor_color, (ascensor_x, ascensor_y, ascensor_width, ascensor_height), border_radius=6)
    pygame.draw.rect(screen, COLORES["brillo_ascensor"], (ascensor_x, ascensor_y, ascensor_width, ascensor_height), 2, border_radius=6)

# Bucle principal del juego
while True:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_UP:
                if estado_actual == LOBBY:
                    # Mover selección en el lobby
                    persona_seleccionada_lobby = max(0, persona_seleccionada_lobby - 1)
                else:
                    opcion_seleccionada = max(0, opcion_seleccionada - 1)
            elif event.key == pygame.K_DOWN:
                if estado_actual == LOBBY:
                    # Mover selección en el lobby
                    if personas_lobby:
                        persona_seleccionada_lobby = min(len(personas_lobby) - 1, persona_seleccionada_lobby + 1)
                else:
                    opcion_seleccionada = min(len(menus[estado_actual]) - 1, opcion_seleccionada + 1)
            elif event.key == pygame.K_RETURN:
                if estado_actual == LOBBY:
                    seleccionar_persona_lobby()
                else:
                    manejar_seleccion()
            elif event.key == pygame.K_ESCAPE:
                if estado_actual == LOBBY:
                    volver_al_menu_principal()
            elif pygame.K_1 <= event.key <= pygame.K_9:
                if estado_actual != LOBBY: # Solo en menús
                    num = event.key - pygame.K_1
                    if num < len(menus[estado_actual]):
                        opcion_seleccionada = num
                        manejar_seleccion()
        elif event.type == pygame.MOUSEMOTION:
            if estado_actual != LOBBY: # Solo en menús
                mouse_x, mouse_y = event.pos
                opciones = menus[estado_actual]
                altura_opcion = 60 if len(opciones) == 4 else 70
                for i in range(len(opciones)):
                    y = panel_top + 120 + i * altura_opcion
                    if panel_left + 40 < mouse_x < panel_left + panel_width - 40 and y < mouse_y < y + 50:
                        opcion_seleccionada = i
        elif event.type == pygame.MOUSEBUTTONDOWN:
            if estado_actual != LOBBY: # Solo en menús
                if event.button == 1:
                    manejar_seleccion()
                    
    # Animación del ascensor (solo en menús)
    if estado_actual != LOBBY:
        altura_opcion = 60 if len(menus[estado_actual]) == 4 else 70
        ascensor_target_y = panel_top + 120 + opcion_seleccionada * altura_opcion + 10
        ascensor_y += (ascensor_target_y - ascensor_y) * 0.2
    # Limpiar mensaje temporal si ha expirado
    if tiempo_mensaje > 0 and time.time() > tiempo_mensaje:
        mensaje_temporal = ""
        tiempo_mensaje = 0
    dibujar_interfaz()
    pygame.display.flip()
    clock.tick(60)