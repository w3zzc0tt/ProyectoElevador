import pygame
import random

class TemporizadorBase:
    def __init__(self, duracion_segundos):
        self.duracion_total = duracion_segundos
        self.tiempo_restante = duracion_segundos
        self.activo = False
        self.tiempo_inicio = 0
        
    def iniciar(self):
        self.activo = True
        self.tiempo_inicio = pygame.time.get_ticks()
        
    def actualizar(self):
        if self.activo:
            tiempo_transcurrido = (pygame.time.get_ticks() - self.tiempo_inicio) / 1000
            self.tiempo_restante = max(0, self.duracion_total - tiempo_transcurrido)
            if self.tiempo_restante <= 0:
                self.activo = False
                return True  # Temporizador terminado
        return False
    
    def obtener_porcentaje(self):
        if self.duracion_total == 0:
            return 0
        return max(0, min(1, self.tiempo_restante / self.duracion_total))
    
    def obtener_tiempo_formateado(self):
        minutos = int(self.tiempo_restante // 60)
        segundos = int(self.tiempo_restante % 60)
        return f"{minutos:02d}:{segundos:02d}"

class TemporizadorTrabajador(TemporizadorBase):
    def __init__(self):
        duracion = random.randint(30, 90)  # 30-90 segundos
        super().__init__(duracion)
        
    def dibujar_barra(self, screen, x, y, ancho=60, alto=6, colores=None):
        # Usa colores por defecto si no se pasan o faltan claves
        default_colores = {
            "fondo": (50, 50, 50),
            "lleno": (0, 255, 100),
            "advertencia": (255, 100, 100)
        }
        if colores is None:
            colores = default_colores
        else:
            # Asegura que existan todas las claves necesarias
            for clave in default_colores:
                if clave not in colores:
                    colores[clave] = default_colores[clave]

        # Fondo de la barra
        pygame.draw.rect(screen, colores["fondo"], (x, y, ancho, alto))
        
        # Barra llena según porcentaje
        porcentaje = self.obtener_porcentaje()
        if porcentaje > 0.3:
            color_barra = colores["lleno"]
        else:
            color_barra = colores["advertencia"]
            
        ancho_lleno = int(ancho * porcentaje)
        if ancho_lleno > 0:
            pygame.draw.rect(screen, color_barra, (x, y, ancho_lleno, alto))

class TemporizadorGameplay(TemporizadorBase):
    def __init__(self):
        super().__init__(5)  # 3.5 minutos = 210 segundos
        
    def dibujar_temporizador_principal(self, screen, fuente, colores, ancho_pantalla):
        tiempo_texto = self.obtener_tiempo_formateado()
        color_texto = colores.get("texto_activo", (255, 255, 255))
        
        # Fondo del temporizador
        barra_ancho = 200
        barra_alto = 30
        barra_x = ancho_pantalla // 2 - barra_ancho // 2
        barra_y = 10
        
        # Fondo oscuro
        pygame.draw.rect(screen, (30, 30, 30), (barra_x - 5, barra_y - 5, barra_ancho + 10, barra_alto + 10))
        pygame.draw.rect(screen, (50, 50, 50), (barra_x, barra_y, barra_ancho, barra_alto))
        
        # Barra de progreso
        porcentaje = self.obtener_porcentaje()
        color_barra = (0, 255, 100) if porcentaje > 0.3 else (255, 100, 100)
        ancho_lleno = int(barra_ancho * porcentaje)
        pygame.draw.rect(screen, color_barra, (barra_x, barra_y, ancho_lleno, barra_alto))
        
        # Texto del tiempo
        texto = fuente.render(tiempo_texto, True, color_texto)
        texto_x = barra_x + barra_ancho // 2 - texto.get_width() // 2
        texto_y = barra_y + barra_alto // 2 - texto.get_height() // 2
        screen.blit(texto, (texto_x, texto_y))
