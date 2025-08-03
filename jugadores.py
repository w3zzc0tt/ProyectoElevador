import pygame

class PersonaBase:
    def __init__(self, nombre, espacio, imagen_path):
        self.nombre = nombre
        self.espacio = espacio  # Cuánto espacio ocupa en el elevador
        self.imagen_path = imagen_path
        self.imagen = None

    def cargar_imagen(self):
        try:
            imagen_original = pygame.image.load(self.imagen_path).convert_alpha()
            self.imagen = pygame.transform.scale(imagen_original, (60, 60))
        except Exception as e:
            print(f"[ERROR] Imagen no cargada: {self.imagen_path} - {e}")
            self.imagen = None

class PersonaDiscapacitada(PersonaBase):
    def __init__(self):
        super().__init__("Discapacitado", 3, "assets/discapacitado1.png")

class PersonaObesa(PersonaBase):
    def __init__(self):
        super().__init__("Obeso mórbido", 3, "assets/gordomorbido.png")

class PersonaTrabajador(PersonaBase):
    def __init__(self):
        super().__init__("Trabajador", 1, "assets/trabajador1.png")

class PersonaCliente(PersonaBase):
    def __init__(self):
        super().__init__("Cliente", 1, "assets/cliente1.png")
