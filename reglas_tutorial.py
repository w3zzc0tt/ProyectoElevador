import pygame

def mostrar_reglas_tutorial(screen, COLORES, fuente, fuente_pequena, fuente_mediana, ANCHO, ALTO, clock):
    running = True
    
    # Fondo oscuro para las reglas
    fondo = pygame.Surface((ANCHO, ALTO))
    fondo.fill((20, 20, 30))
    
    # Título
    titulo = fuente.render("REGLAS Y TUTORIAL", True, COLORES["verde_led"])
    
    # Texto de reglas organizado por secciones
    secciones = [
        ("REGLAS DEL JUEGO", [
            "• Capacidad del elevador: máximo 9 espacios",
            "• Sistema de prioridad:",
            "  1. Personas con discapacidad (+4 puntos)",
            "  2. Personas obesas (+3 puntos)", 
            "  3. Trabajadores (+2 puntos)",
            "  4. Clientes (+1 punto)",
            "• Penalización: -4 puntos por no atender discapacitados",
            "• Denuncias: Activadas tras 2 penalizaciones"
        ]),
        ("OBJETIVO", [
            "Transportar exitosamente a todas las personas",
            "del lobby a sus destinos correspondientes"
        ]),
        ("CONTROLES", [
            "• Flechas ← → : Mover selección de personas",
            "• ENTER: Subir persona seleccionada al elevador",
            "• ESPACIO: Continuar con el ascensor",
            "• ESC: Volver al menú principal"
        ]),
        ("FLUJO DEL JUEGO", [
            "1. Lobby: Seleccionar personas para subir",
            "2. Ascensor: Transportar automáticamente",
            "3. Finalización: Cuando todos hayan sido transportados"
        ])
    ]
    
    # Pre-renderizar todas las superficies para evitar superposiciones
    elementos_renderizados = []
    y_actual = 80
    
    for titulo_seccion, lineas in secciones:
        # Título de sección
        titulo_surface = fuente_mediana.render(titulo_seccion, True, COLORES["verde_led"])
        elementos_renderizados.append((titulo_surface, ANCHO//2 - titulo_surface.get_width()//2, y_actual, True))
        y_actual += titulo_surface.get_height() + 10
        
        # Líneas de contenido
        for linea in lineas:
            linea_surface = fuente_pequena.render(linea, True, COLORES["texto_activo"])
            elementos_renderizados.append((linea_surface, 50, y_actual, False))
            y_actual += linea_surface.get_height() + 5
        
        # Espacio entre secciones
        y_actual += 20
    
    # Instrucción final
    instruccion = fuente_pequena.render("Presiona ESC para volver al menú principal", True, COLORES["verde_led_claro"])
    elementos_renderizados.append((instruccion, ANCHO//2 - instruccion.get_width()//2, y_actual, True))
    
    # Calcular scroll
    altura_total = y_actual + 50
    scroll_y = 0
    scroll_speed = 25
    max_scroll = max(0, altura_total - ALTO + 100)
    
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                return "salir"
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    running = False
                elif event.key == pygame.K_UP:
                    scroll_y = max(scroll_y - scroll_speed, 0)
                elif event.key == pygame.K_DOWN:
                    scroll_y = min(scroll_y + scroll_speed, max_scroll)

        # Limpiar pantalla
        screen.blit(fondo, (0, 0))
        
        # Dibujar título fijo
        screen.blit(titulo, (ANCHO//2 - titulo.get_width()//2, 20))
        
        # Dibujar elementos con scroll
        for surface, x, y, centrado in elementos_renderizados:
            y_pos = y - scroll_y
            if 60 <= y_pos <= ALTO - 30:  # Solo dibujar si está en pantalla
                screen.blit(surface, (x, y_pos))
        
        # Instrucciones de navegación
        if max_scroll > 0:
            nav_text = fuente_pequena.render("↑↓ Desplazar | ESC Volver", True, COLORES["verde_led_claro"])
        else:
            nav_text = fuente_pequena.render("ESC para volver", True, COLORES["verde_led_claro"])
        screen.blit(nav_text, (ANCHO//2 - nav_text.get_width()//2, ALTO - 40))

        pygame.display.flip()
        clock.tick(60)

    return "menu"
