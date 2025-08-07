import pygame

def manejar_menu(screen, COLORES, fuente, fuente_led, panel_surface_oscura, ANCHO, ALTO, clock):
    # 🔊 Cargar y reproducir música del menú al inicio (si no está sonando)
    if not pygame.mixer.music.get_busy():
        try:
            pygame.mixer.music.load("assets/menu_soundtrack.mp3")
            pygame.mixer.music.play(-1)  # Bucle infinito
            print("🎵 Música del menú iniciada")
        except pygame.error as e:
            print(f"❌ Error al cargar menu_soundtrack.mp3: {e}")

    fondo = pygame.image.load("assets/elevator.jpg").convert()
    fondo = pygame.transform.scale(fondo, (ANCHO, ALTO))

    panel_width, panel_height = 400, 440
    panel_left = (ANCHO - panel_width) // 2
    panel_top = (ALTO - panel_height) // 2
    ascensor_width, ascensor_height = 24, 24
    ascensor_x = panel_left - 40
    ascensor_y = panel_top + 40
    ascensor_color = COLORES["ascensor"]
    ascensor_y_animado = ascensor_y

    menus = ["1. Jugar", "2. R & T", "3. Config", "4. Salir"]
    opcion_seleccionada = 0

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                return "salir"
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_UP:
                    opcion_seleccionada = max(0, opcion_seleccionada - 1)
                elif event.key == pygame.K_DOWN:
                    opcion_seleccionada = min(len(menus) - 1, opcion_seleccionada + 1)
                elif event.key == pygame.K_RETURN:
                    if opcion_seleccionada == 0:
                        pygame.mixer.music.stop()  # 🛑 Detener música del menú
                        print("⏹️ Música del menú detenida al iniciar el juego")
                        return "FACIL"
                    elif opcion_seleccionada == 1:
                        return "reglas"
                    elif opcion_seleccionada == 2:
                        return "config"
                    elif opcion_seleccionada == 3:
                        return "salir"
                elif pygame.K_1 <= event.key <= pygame.K_4:
                    indice = event.key - pygame.K_1
                    if indice < len(menus):
                        opcion_seleccionada = indice
                        if indice == 0:
                            pygame.mixer.music.stop()  # 🛑 Detener música del menú
                            print("⏹️ Música del menú detenida al iniciar el juego")
                            return "FACIL"
                        elif indice == 1:
                            return "reglas"
                        elif indice == 2:
                            return "config"
                        elif indice == 3:
                            return "salir"
            elif event.type == pygame.MOUSEMOTION:
                mouse_x, mouse_y = event.pos
                for i in range(len(menus)):
                    y = panel_top + 120 + i * 70
                    if panel_left + 40 < mouse_x < panel_left + panel_width - 40 and y < mouse_y < y + 50:
                        opcion_seleccionada = i
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:
                    if opcion_seleccionada == 0:
                        pygame.mixer.music.stop()  # 🛑 Detener música del menú
                        print("⏹️ Música del menú detenida al iniciar el juego")
                        return "FACIL"
                    elif opcion_seleccionada == 1:
                        return "reglas"
                    elif opcion_seleccionada == 2:
                        return "config"
                    elif opcion_seleccionada == 3:
                        return "salir"

        # Dibujar fondo completo y capa oscura
        screen.blit(fondo, (0, 0))
        screen.blit(panel_surface_oscura, (0, 0))

        # Dibujar panel
        pygame.draw.rect(screen, COLORES["panel_interior"], (panel_left, panel_top, panel_width, panel_height), border_radius=15)
        pygame.draw.rect(screen, COLORES["borde_panel"], (panel_left, panel_top, panel_width, panel_height), 3, border_radius=15)

        # Display verde
        display_rect = pygame.Rect(panel_left + 30, panel_top + 30, panel_width - 60, 70)
        pygame.draw.rect(screen, COLORES["display_fondo"], display_rect, border_radius=8)
        pygame.draw.rect(screen, COLORES["display_borde"], display_rect, 2, border_radius=8)
        piso_txt = fuente_led.render(str(opcion_seleccionada + 1), True, COLORES["verde_led"])
        screen.blit(piso_txt, (display_rect.centerx - piso_txt.get_width() // 2, display_rect.centery - piso_txt.get_height() // 2))

        # Opciones
        for i, opcion in enumerate(menus):
            y = panel_top + 120 + i * 70
            rect_opcion = pygame.Rect(panel_left + 40, y, panel_width - 80, 50)
            if i == opcion_seleccionada:
                pygame.draw.rect(screen, COLORES["opcion_activa"], rect_opcion, border_radius=10)
                pygame.draw.rect(screen, COLORES["borde_opcion"], rect_opcion, 2, border_radius=10)
            else:
                pygame.draw.rect(screen, COLORES["opcion_inactiva"], rect_opcion, border_radius=10)
            color_texto = COLORES["texto_activo"] if i == opcion_seleccionada else COLORES["texto_inactivo"]
            texto = fuente.render(opcion, True, color_texto)
            screen.blit(texto, (rect_opcion.x + 50, rect_opcion.centery - texto.get_height() // 2))

            # LED
            led_rect = pygame.Rect(rect_opcion.x + 15, rect_opcion.centery - 10, 20, 20)
            pygame.draw.rect(screen, (20, 20, 20), led_rect, border_radius=10)
            if i == opcion_seleccionada:
                pygame.draw.rect(screen, COLORES["verde_led"], led_rect, border_radius=10)
                pygame.draw.rect(screen, COLORES["verde_led_claro"], led_rect, 2, border_radius=10)

        # Animación ascensor
        ascensor_target_y = panel_top + 120 + opcion_seleccionada * 70 + 10
        ascensor_y_animado += (ascensor_target_y - ascensor_y_animado) * 0.2
        pygame.draw.rect(screen, COLORES["sombra_ascensor"], (ascensor_x - 6, ascensor_y_animado - 6, ascensor_width + 12, ascensor_height + 12), border_radius=8)
        pygame.draw.rect(screen, ascensor_color, (ascensor_x, ascensor_y_animado, ascensor_width, ascensor_height), border_radius=6)
        pygame.draw.rect(screen, COLORES["brillo_ascensor"], (ascensor_x, ascensor_y_animado, ascensor_width, ascensor_height), 2, border_radius=6)

        pygame.display.flip()
        clock.tick(60)

